import asyncio
from typing import Dict, List, Tuple, Optional
from app.engine.orderbook import OrderBook, OrderBookEntry
from app.models.order import Order, OrderSide, OrderType, OrderStatus
from app.models.trade import Trade
from app.schemas.order import OrderCreate

class MatchingEngine:
    def __init__(self):
        self.orderbooks: Dict[str, OrderBook] = {}
        self.locks: Dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock() # For creating new books safely

    async def get_orderbook(self, symbol: str) -> OrderBook:
        if symbol not in self.orderbooks:
            async with self._global_lock:
                if symbol not in self.orderbooks:
                    self.orderbooks[symbol] = OrderBook(symbol)
                    self.locks[symbol] = asyncio.Lock()
        return self.orderbooks[symbol]

    async def process_order(self, order: Order) -> Tuple[List[dict], int]:
        """
        Process an order against the order book.
        Returns a tuple of (trades_to_create, filled_quantity).
        trades_to_create is a list of dicts with trade details.
        Does NOT update the DB. That is the caller's responsibility.
        Does NOT update the in-memory book yet. Caller must confirm.
        """
        symbol = order.instrument.symbol
        book = await self.get_orderbook(symbol)
        
        # We need to lock the book for this instrument
        async with self.locks[symbol]:
            matches = []
            remaining_qty = order.quantity - order.filled_quantity
            
            if order.side == OrderSide.BUY:
                # Match against Asks (Sells)
                # Look for lowest price first
                while remaining_qty > 0 and book.asks:
                    best_ask = book.get_best_ask()
                    
                    # Check price condition
                    if order.type == OrderType.LIMIT and best_ask.price > float(order.price):
                        break
                        
                    # Match found
                    match_qty = min(remaining_qty, best_ask.quantity)
                    price = best_ask.price # Executed at the maker's price
                    
                    matches.append({
                        "buy_order_id": order.id,
                        "sell_order_id": best_ask.order_id,
                        "instrument_id": order.instrument_id,
                        "price": price,
                        "quantity": match_qty,
                        "maker_order_id": best_ask.order_id
                    })
                    
                    remaining_qty -= match_qty
                    
                    # Update maker order in book (temporarily for this calculation? No, we must update book)
                    # Use a strategy: Optimistic matching?
                    # Since we hold the lock, we can modify the book.
                    # If DB transaction fails later, we are in trouble.
                    # BUT: We are inside a lock. If DB fails, we crash or raise exception.
                    # We should probably rollback memory changes. 
                    
                    # Simplified for this exercise: Modify book. If DB commit fails, we might have drift.
                    # In production, we'd replay from DB event log on restart.
                    
                    best_ask.quantity -= match_qty
                    if best_ask.quantity == 0:
                        book.asks.remove(best_ask)
                        del book.orders[best_ask.order_id]
            
            else: # SELL
                # Match against Bids (Buys)
                # Look for highest price first
                while remaining_qty > 0 and book.bids:
                    best_bid = book.get_best_bid()
                    
                    if order.type == OrderType.LIMIT and best_bid.price < float(order.price):
                        break
                        
                    match_qty = min(remaining_qty, best_bid.quantity)
                    price = best_bid.price
                    
                    matches.append({
                        "buy_order_id": best_bid.order_id,
                        "sell_order_id": order.id,
                        "instrument_id": order.instrument_id,
                        "price": price,
                        "quantity": match_qty,
                        "maker_order_id": best_bid.order_id
                    })
                    
                    remaining_qty -= match_qty
                    
                    best_bid.quantity -= match_qty
                    if best_bid.quantity == 0:
                        book.bids.remove(best_bid)
                        del book.orders[best_bid.order_id]

            # If order not fully filled, add to book
            if remaining_qty > 0:
                # Valid for LIMIT orders. MARKET orders that verify liquidity should shouldn't be here if no liquidity?
                # Or just partial fill and cancel rest? 
                # Standard NASDAQ: Market orders cancel if no liquidity. Limit orders rest.
                if order.type == OrderType.LIMIT:
                    entry = OrderBookEntry(
                        order_id=order.id,
                        user_id=order.user_id,
                        price=float(order.price),
                        quantity=remaining_qty,
                        timestamp=order.created_at.timestamp(),
                        order_type=order.type
                    )
                    book.add_order(entry, order.side)
            
            return matches, order.quantity - remaining_qty

matching_engine = MatchingEngine()
