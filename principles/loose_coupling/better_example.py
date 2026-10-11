"""
================================================================================
1. BAD CODE: THE ORDER SERVICE THAT CALLS EVERYONE DIRECTLY
================================================================================
CRITIQUE: OrderService knows about Email, Inventory, and Analytics. A crash in
analytics aborts the whole order, and each new reaction means editing checkout.
"""

class EmailService:
    def send_confirmation(self, order_id: str) -> None: print(f"[Email] confirmation for {order_id}")

class InventoryService:
    def reserve(self, order_id: str) -> None: print(f"[Inventory] reserved stock for {order_id}")

class AnalyticsService:
    def track(self, order_id: str) -> None: raise ConnectionError("analytics vendor is down")


class BadOrderService:
    def __init__(self):
        self.email = EmailService()
        self.inventory = InventoryService()
        self.analytics = AnalyticsService()

    def place_order(self, order_id: str) -> bool:
        self.inventory.reserve(order_id)
        self.email.send_confirmation(order_id)
        self.analytics.track(order_id)    # ❌ raises => customer sees an error after paying
        return True


"""
================================================================================
2. THE PRINCIPLE: "STRIVE FOR LOOSELY COUPLED DESIGNS"
================================================================================
What Varies:
    The set of things that must happen AFTER an order is placed.

What Stays Stable:
    The fact that "an order was placed" and the order data itself.
"""


"""
================================================================================
3. GOOD CODE: AN EVENT BUS BETWEEN PUBLISHER AND SUBSCRIBERS
================================================================================
"""
from collections import defaultdict
from typing import Callable, Dict, List

# ------------------------------------------------------------------------------
# APPROACH A: EVENT BUS (Publish / Subscribe)
# ------------------------------------------------------------------------------

Handler = Callable[[dict], None]

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Handler]] = defaultdict(list)

    def subscribe(self, event: str, handler: Handler) -> None:
        self._subscribers[event].append(handler)

    def unsubscribe(self, event: str, handler: Handler) -> None:
        self._subscribers[event].remove(handler)

    def publish(self, event: str, payload: dict) -> None:
        for handler in list(self._subscribers[event]):
            try:
                handler(payload)
            except Exception as exc:  # One bad subscriber must not break the others
                name = getattr(handler, "__name__", repr(handler))
                print(f"[EventBus] handler '{name}' failed: {exc}")


class OrderService:
    """Knows only the bus and the event name. Not Email, Inventory, or Analytics."""
    def __init__(self, bus: EventBus):
        self._bus = bus

    def place_order(self, order_id: str) -> bool:
        self._bus.publish("order_placed", {"order_id": order_id})
        return True


# ------------------------------------------------------------------------------
# APPROACH B: INDEPENDENT SUBSCRIBERS (each lives in its own module/team)
# ------------------------------------------------------------------------------

def send_confirmation_email(payload: dict) -> None:
    print(f"[Email] confirmation for {payload['order_id']}")

def reserve_stock(payload: dict) -> None:
    print(f"[Inventory] reserved stock for {payload['order_id']}")

def track_analytics(payload: dict) -> None:
    raise ConnectionError("analytics vendor is down")


"""
================================================================================
4. WHAT IT SOLVES IN REALITY: MONETARY AND PRODUCTION BREAKDOWN
================================================================================

PROBLEM 1: A NON-CRITICAL FAILURE KILLS REVENUE
-----------------------------------------------
- THE MESSY REALITY: The analytics vendor goes down on Black Friday. BadOrderService raises
  after taking payment; customers retry, get double charged, support melts down.
- THE SOLUTION: The bus isolates handler failures. The order succeeds; analytics is logged
  and fixed later.

PROBLEM 2: NEW REACTIONS WITHOUT TOUCHING CHECKOUT
--------------------------------------------------
- THE MESSY REALITY: Growth wants a loyalty-points update; Finance wants a fraud check.
  Each is another edit to the most sensitive file in the company.
- THE SOLUTION: bus.subscribe("order_placed", add_loyalty_points). Checkout is unchanged.

PROBLEM 3: TEAM INDEPENDENCE
----------------------------
- THE MESSY REALITY: OrderService imports five other teams' classes; any of their API
  changes break your build.
- THE SOLUTION: Teams only agree on the event's name and payload shape.

PROBLEM 4: TESTING CHECKOUT ALONE
---------------------------------
- THE MESSY REALITY: Testing place_order() requires real email, inventory, and analytics.
- THE SOLUTION: Give OrderService a bus with one recording handler.
"""

if __name__ == "__main__":
    print("--- Bad (tightly coupled) ---")
    try:
        BadOrderService().place_order("A-1")
    except ConnectionError as e:
        print("Order FAILED after payment:", e)

    print("\n--- Good (loosely coupled) ---")
    bus = EventBus()
    bus.subscribe("order_placed", reserve_stock)
    bus.subscribe("order_placed", send_confirmation_email)
    bus.subscribe("order_placed", track_analytics)
    print("Order placed:", OrderService(bus).place_order("A-2"))
