from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.order import Order, OrderSide, OrderType, OrderStatus
from app.models.user import User, Account
from app.models.instrument import Instrument
from app.models.trade import Trade, Holding
from app.schemas.order import OrderCreate
from app.services.matching_engine import matching_engine
from app.exceptions import InsufficientFundsError, InstrumentNotFoundError, InsufficientHoldingsError

async def create_order(db: AsyncSession, order_in: OrderCreate, user: User):
    # 1. Validate Instrument
    result = await db.execute(select(Instrument).where(Instrument.symbol == order_in.instrument_symbol.upper()))
    instrument = result.scalars().first()
    if not instrument:
        raise InstrumentNotFoundError(f"Instrument {order_in.instrument_symbol} not found")

    # 2. Validate Funds/Holdings & Lock Funds
    # We need to lock the account or holding row to prevent race conditions
    # For MVP, we'll just check and update in transaction. Serailizable isolation or row locking needed for production.
    
    if order_in.side == OrderSide.BUY:
        # Check cash balance
        cost = order_in.price * order_in.quantity # Logic for MARKET orders? 
        # Market orders need estimated price. For now, assume LIMIT or reject MARKET without price (simplified)
        # Or take current market price + buffer. Standard practice is to reject if no funds for estimated cost.
        
        if order_in.type == OrderType.MARKET:
            # Simplified: Reject market orders for now or treat as Limit with high price?
            # Let's require price for now to simplify, or fetch current price.
            # IF using MARKET, we'd need to peek at orderbook for best price.
            if not order_in.price:
                # Get best ask
                book = await matching_engine.get_orderbook(instrument.symbol)
                best_ask = book.get_best_ask()
                if not best_ask:
                    raise ValueError("No liquidity for market order")
                estimated_price = best_ask.price
            else:
                 estimated_price = order_in.price
            cost = estimated_price * order_in.quantity

        if user.account.cash_balance < cost:
            raise InsufficientFundsError(f"Insufficient funds. Required: {cost}, Available: {user.account.cash_balance}")
        
        # Deduct cash (Hold it)
        user.account.cash_balance -= cost
        db.add(user.account)

    else: # SELL
        # Check holdings
        result = await db.execute(select(Holding).where(Holding.user_id == user.id, Holding.instrument_id == instrument.id))
        holding = result.scalars().first()
        if not holding or holding.quantity < order_in.quantity:
             raise InsufficientHoldingsError(f"Insufficient holdings for {instrument.symbol}")
        
        # Deduct holdings (Hold them)
        holding.quantity -= order_in.quantity
        db.add(holding)

    # 3. Create Order
    db_order = Order(
        user_id=user.id,
        instrument_id=instrument.id,
        side=order_in.side,
        type=order_in.type,
        price=order_in.price,
        quantity=order_in.quantity,
        status=OrderStatus.OPEN
    )
    db_order.instrument = instrument
    db_order.user = user
    db.add(db_order)
    await db.flush() # Get ID
    await db.refresh(db_order)
    db_order.instrument = instrument
    db_order.user = user
    
    # 4. Match Order
    # This might need to happen AFTER commit if we want to ensure order is persisted before matching?
    # But we want atomic trade execution.
    # So we match in memory, get proposed trades, and write them to DB in same transaction.
    
    matches, filled_qty = await matching_engine.process_order(db_order)
    
    # 5. Apply Matches
    for match in matches:
        # Create Trade
        trade = Trade(
            buy_order_id=match["buy_order_id"],
            sell_order_id=match["sell_order_id"],
            instrument_id=instrument.id,
            price=match["price"],
            quantity=match["quantity"]
        )
        db.add(trade)
        
        # Update Makers (Passive orders)
        # We need to fetch the maker order from DB to update its status
        # Since we might have multiple makers, loop them.
        maker_order_id = match["maker_order_id"]
        result = await db.execute(select(Order).where(Order.id == maker_order_id))
        maker_order = result.scalars().first()
        
        maker_order.filled_quantity += match["quantity"]
        if maker_order.filled_quantity == maker_order.quantity:
            maker_order.status = OrderStatus.FILLED
        else:
            maker_order.status = OrderStatus.PARTIALLY_FILLED
        db.add(maker_order)
        
        # Update Taker (Current Order)
        # We update it at the end, or cumulatively
        # Also need to settle funds for the TRADE
        
        # Buyer: Already paid 'cost'. If bought at better price, refund difference.
        # Seller: Receive cash.
        
        buy_order = db_order if db_order.side == OrderSide.BUY else maker_order
        sell_order = db_order if db_order.side == OrderSide.SELL else maker_order
        
        # Seller gets cash
        # Need to fetch seller account. If seller is current user, we have it. If not, fetch.
        if sell_order.user_id == user.id:
            seller_account = user.account
        else:
            result = await db.execute(select(Account).where(Account.user_id == sell_order.user_id))
            seller_account = result.scalars().first()
        
        trade_value = match["price"] * match["quantity"]
        seller_account.cash_balance += trade_value
        db.add(seller_account)
        
        # Buyer gets Instrument
        # Fetch buyer holding
        if buy_order.user_id == user.id:
            buyer_id = user.id
        else:
            buyer_id = buy_order.user_id
            
        result = await db.execute(select(Holding).where(Holding.user_id == buyer_id, Holding.instrument_id == instrument.id))
        buyer_holding = result.scalars().first()
        if not buyer_holding:
            buyer_holding = Holding(user_id=buyer_id, instrument_id=instrument.id, quantity=0)
            db.add(buyer_holding)
        
        buyer_holding.quantity += match["quantity"]
        db.add(buyer_holding)

    # 6. Update Taker Order Status
    db_order.filled_quantity = filled_qty
    if db_order.filled_quantity == db_order.quantity:
        db_order.status = OrderStatus.FILLED
    elif db_order.filled_quantity > 0:
        db_order.status = OrderStatus.PARTIALLY_FILLED
    else:
        db_order.status = OrderStatus.OPEN
    
    db.add(db_order)
    
    await db.commit()
    await db.refresh(db_order)
    
    # 7. Publish Events (Fire and forget, or background task)
    from app.services.event import publish_trade, publish_orderbook_update
    
    # Publish Trades
    for match in matches:
        trade_event = {
            "symbol": instrument.symbol,
            "price": float(match["price"]),
            "quantity": match["quantity"],
            "timestamp": db_order.created_at.timestamp()
        }
        await publish_trade(trade_event, instrument.symbol)
    
    # Publish OrderBook Update
    # We need to get the current depth. 
    book = await matching_engine.get_orderbook(instrument.symbol)
    depth = book.depth()
    await publish_orderbook_update(instrument.symbol, depth)
    
    return db_order

async def get_user_orders(db: AsyncSession, user_id: int):
    result = await db.execute(select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc()))
    return result.scalars().all()
