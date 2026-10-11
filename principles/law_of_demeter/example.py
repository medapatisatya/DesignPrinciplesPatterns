"""
================================================================================
1. BAD CODE: TRAIN-WRECK CHAINS (THE RUSHED MVP)
================================================================================
The Cashier reaches through Customer -> Wallet -> balance to do its job.
"""

class BadWallet:
    def __init__(self, balance: float): self.balance = balance
    def get_balance(self) -> float: return self.balance
    def set_balance(self, value: float) -> None: self.balance = value

class BadCustomer:
    def __init__(self, name: str, wallet: BadWallet):
        self.name = name
        self._wallet = wallet
    def get_wallet(self) -> BadWallet: return self._wallet


class BadCashier:
    def checkout(self, customer: BadCustomer, amount: float) -> str:
        # ❌ CRITICAL ERROR: Cashier knows Customer HAS a wallet, that the wallet has a
        # balance, and how to mutate it. It talks to a stranger (Wallet).
        if customer.get_wallet().get_balance() >= amount:
            customer.get_wallet().set_balance(customer.get_wallet().get_balance() - amount)
            return "PAID"
        return "DECLINED"


"""
================================================================================
2. THE PRINCIPLE: "ONLY TALK TO YOUR IMMEDIATE FRIENDS" (LAW OF DEMETER)
================================================================================
Core Definition:
    A method should only call methods on:
      1. `self`
      2. its parameters
      3. objects it creates
      4. its direct components (attributes)
    Never on objects returned by those calls (strangers).

The Golden Rule:
    If you see a.get_b().get_c().do_x(), tell `a` what you want instead
    ("tell, don't ask") and let `a` delegate.
"""


"""
================================================================================
3. GOOD CODE: TELL, DON'T ASK
================================================================================
"""
# ------------------------------------------------------------------------------
# APPROACH A: DELEGATION (the owner exposes the behavior, hides the structure)
# ------------------------------------------------------------------------------

class Wallet:
    def __init__(self, balance: float):
        self._balance = balance

    def debit(self, amount: float) -> bool:
        if amount > self._balance:
            return False
        self._balance -= amount
        return True


class Customer:
    def __init__(self, name: str, wallet: Wallet):
        self.name = name
        self._wallet = wallet

    def pay(self, amount: float) -> bool:
        return self._wallet.debit(amount)      # Customer talks to ITS friend only


class Cashier:
    def checkout(self, customer: Customer, amount: float) -> str:
        return "PAID" if customer.pay(amount) else "DECLINED"   # one friend, one dot


# ------------------------------------------------------------------------------
# APPROACH B: PASS ONLY THE DATA NEEDED (narrow parameters)
# ------------------------------------------------------------------------------

def format_greeting(customer_name: str) -> str:
    """Takes a str, not the whole Customer, so it can't wander into its internals."""
    return f"Welcome back, {customer_name}!"


"""
================================================================================
4. WHAT IT SOLVES IN REALITY: UNABRIDGED PRODUCTION BREAKDOWN
================================================================================

PROBLEM 1: RIPPLE EFFECTS OF REFACTORING
----------------------------------------
- THE MESSY REALITY: Finance replaces 'Wallet' with 'PaymentMethods' (card + wallet +
  credit). Every chain like customer.get_wallet().get_balance() across the codebase
  breaks, in dozens of files.
- THE SOLUTION: Only Customer.pay() changes. Callers never knew a wallet existed.

PROBLEM 2: BROKEN INVARIANTS
----------------------------
- THE MESSY REALITY: BadCashier mutates the wallet balance directly, bypassing rules such as
  overdraft limits or audit logs.
- THE SOLUTION: Wallet.debit() owns the rule in one place.

PROBLEM 3: PAINFUL MOCKING
--------------------------
- THE MESSY REALITY: To test BadCashier you must build Customer -> Wallet -> balance mocks
  three layers deep.
- THE SOLUTION: Mock a single object with a single method: pay().

PROBLEM 4: HIDDEN NULL-POINTER LANDMINES
----------------------------------------
- THE MESSY REALITY: a.b().c().d() fails with AttributeError if any link is None, and
  every caller must guard each link.
- THE SOLUTION: The owner handles its own structure and edge cases once.
"""

if __name__ == "__main__":
    print("--- Bad chain ---")
    print(BadCashier().checkout(BadCustomer("Ada", BadWallet(50)), 20))

    print("\n--- Good delegation ---")
    ada = Customer("Ada", Wallet(50))
    print(Cashier().checkout(ada, 20))
    print(Cashier().checkout(ada, 40))

    print("\n--- Narrow parameter ---")
    print(format_greeting(ada.name))
