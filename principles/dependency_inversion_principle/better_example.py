"""
================================================================================
1. BAD CODE: THE ORDER SERVICE THAT BUILDS ITS OWN INFRASTRUCTURE
================================================================================
CRITIQUE: Business rules are fused to Stripe and a SQL database. You cannot
run, test, or change them without the real infrastructure.
"""

class StripeClient:
    def charge_card(self, amount: float) -> bool:
        print(f"[Stripe] charging ${amount}")
        return True

class MySqlConnection:
    def execute(self, sql: str) -> None:
        print(f"[MySQL] {sql}")


class BadOrderService:
    def __init__(self):
        self.stripe = StripeClient()          # ❌ concrete
        self.db = MySqlConnection()           # ❌ concrete

    def place_order(self, order_id: str, amount: float) -> bool:
        if self.stripe.charge_card(amount):
            self.db.execute(f"INSERT INTO orders VALUES ('{order_id}', 'PAID')")  # ❌ also SQL injection-prone
            return True
        return False


"""
================================================================================
2. THE PRINCIPLE: "DEPEND ON ABSTRACTIONS"
================================================================================
What Varies:
    Payment provider and persistence technology.

What Stays Stable:
    The business rule: charge first; record the order as PAID only if the charge
    succeeds; otherwise record FAILED.
"""


"""
================================================================================
3. GOOD CODE: OrderService DEPENDS ON TWO ABSTRACTIONS, WIRED AT THE EDGE
================================================================================
"""
from abc import ABC, abstractmethod
from typing import Dict

# ------------------------------------------------------------------------------
# APPROACH A: ABSTRACTIONS OWNED BY THE BUSINESS LAYER
# ------------------------------------------------------------------------------

class PaymentProcessor(ABC):
    @abstractmethod
    def charge(self, amount: float) -> bool: ...

class OrderRepository(ABC):
    @abstractmethod
    def save(self, order_id: str, status: str) -> None: ...

    @abstractmethod
    def status_of(self, order_id: str) -> str: ...


class OrderService:
    """High-level policy. No Stripe, no SQL, no imports of infrastructure."""
    def __init__(self, payments: PaymentProcessor, orders: OrderRepository):
        self._payments = payments
        self._orders = orders

    def place_order(self, order_id: str, amount: float) -> bool:
        ok = self._payments.charge(amount)
        self._orders.save(order_id, "PAID" if ok else "FAILED")
        return ok


# --- Low-level details: they depend on (implement) the abstractions ----------
class StripeProcessor(PaymentProcessor):
    def charge(self, amount: float) -> bool:
        print(f"[Stripe] charging ${amount}")
        return True

class InMemoryOrderRepository(OrderRepository):
    def __init__(self): self._rows: Dict[str, str] = {}
    def save(self, order_id: str, status: str) -> None: self._rows[order_id] = status
    def status_of(self, order_id: str) -> str: return self._rows[order_id]

class SqlOrderRepository(OrderRepository):
    def __init__(self): self._rows: Dict[str, str] = {}
    def save(self, order_id: str, status: str) -> None:
        print(f"[SQL] UPSERT orders({order_id!r}, {status!r})  -- parameterised")
        self._rows[order_id] = status
    def status_of(self, order_id: str) -> str: return self._rows[order_id]


# ------------------------------------------------------------------------------
# APPROACH B: THE COMPOSITION ROOT (the ONLY place concretes are named)
# ------------------------------------------------------------------------------

def build_order_service(env: str) -> OrderService:
    if env == "prod":
        return OrderService(StripeProcessor(), SqlOrderRepository())
    return OrderService(StripeProcessor(), InMemoryOrderRepository())


"""
================================================================================
4. WHAT IT SOLVES IN REALITY: MONETARY AND PRODUCTION BREAKDOWN
================================================================================

PROBLEM 1: PAYMENT PROVIDER OUTAGE OR REPRICING
-----------------------------------------------
- THE MESSY REALITY: Stripe raises fees 20%. Moving to Adyen means rewriting OrderService,
  where payment and persistence logic are tangled.
- THE SOLUTION: Implement AdyenProcessor(PaymentProcessor) and change one line in
  build_order_service().

PROBLEM 2: TESTING THE FAILURE PATH
-----------------------------------
- THE MESSY REALITY: How do you make real Stripe decline a card on demand? You mostly can't.
- THE SOLUTION: Inject a FakeProcessor that returns False and assert the order is FAILED.

PROBLEM 3: DATABASE MIGRATION
-----------------------------
- THE MESSY REALITY: MySQL -> Postgres touches business code with embedded SQL strings.
- THE SOLUTION: Write a new OrderRepository. Business rules stay byte-for-byte identical.

PROBLEM 4: CIRCULAR / HEAVY IMPORTS
-----------------------------------
- THE MESSY REALITY: Importing OrderService loads the Stripe SDK and DB drivers, slowing
  startup and CI.
- THE SOLUTION: OrderService imports only abc, so it loads instantly anywhere.
"""

if __name__ == "__main__":
    print("--- Dev wiring ---")
    svc = build_order_service("dev")
    svc.place_order("A-1", 49.99)

    print("\n--- Test double wiring ---")
    class DecliningProcessor(PaymentProcessor):
        def charge(self, amount: float) -> bool: return False
    repo = InMemoryOrderRepository()
    OrderService(DecliningProcessor(), repo).place_order("A-2", 10.0)
    print("Status of A-2:", repo.status_of("A-2"))

    print("\n--- Prod wiring ---")
    build_order_service("prod").place_order("A-3", 99.0)
