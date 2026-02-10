from sortedcontainers import SortedList
from typing import List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from app.models.order import OrderSide, OrderType, OrderStatus

@dataclass
class OrderBookEntry:
    order_id: int
    user_id: int
    price: float  # Use float for in-memory speed, convert to Decimal for DB
    quantity: int
    timestamp: float
    order_type: OrderType

    def __eq__(self, other):
        return self.order_id == other.order_id

class OrderBook:
    def __init__(self, symbol: str):
        self.symbol = symbol
        # Asks: Sell orders, sorted by Price ASC, then Time ASC
        self.asks = SortedList(key=lambda x: (x.price, x.timestamp))
        # Bids: Buy orders, sorted by Price DESC, then Time ASC
        # key: (-price, timestamp) ensures highest price comes first
        self.bids = SortedList(key=lambda x: (-x.price, x.timestamp))
        
        # Fast lookup by order_id to support cancellation
        self.orders = {} # order_id -> OrderBookEntry

    def add_order(self, order: OrderBookEntry, side: OrderSide):
        self.orders[order.order_id] = order
        if side == OrderSide.BUY:
            self.bids.add(order)
        else:
            self.asks.add(order)

    def remove_order(self, order_id: int) -> Optional[OrderBookEntry]:
        if order_id in self.orders:
            order = self.orders.pop(order_id)
            # Try removing from both, though we should know the side. 
            # Optimization: could store side in map.
            try:
                self.bids.remove(order)
            except ValueError:
                self.asks.remove(order)
            return order
        return None

    def get_best_bid(self) -> Optional[OrderBookEntry]:
        return self.bids[0] if self.bids else None

    def get_best_ask(self) -> Optional[OrderBookEntry]:
        return self.asks[0] if self.asks else None
        
    def depth(self, depth: int = 10) -> dict:
        return {
            "bids": [{"price": b.price, "qty": b.quantity} for b in self.bids[:depth]],
            "asks": [{"price": a.price, "qty": a.quantity} for a in self.asks[:depth]]
        }
