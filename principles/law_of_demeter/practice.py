"""
================================================================================
CHALLENGE: LAW OF DEMETER (CLEAN SLATE)
================================================================================
PROBLEM CONTEXT:
A Cashier charges Customers. A Customer owns a Wallet. Today the Cashier digs
through customer.get_wallet().get_balance()... Tomorrow wallets might become
cards, credit lines, or loyalty points.

THE GOAL:
The Cashier may talk ONLY to the Customer it receives, and only through
Customer.pay(). The Customer must not expose its wallet publicly.

YOUR MISSION:
1. Implement Wallet.debit.
2. Implement Customer.pay (delegating to its own wallet).
3. Implement Cashier.checkout using ONLY customer.pay().
"""

import unittest

# ==============================================================================
# 🚨 STEP 1: THE BAD CODE (DO NOT USE THIS LOGIC)
# ==============================================================================
class BadCashier:
    def checkout(self, customer, amount: float) -> str:
        if customer.get_wallet().get_balance() >= amount:          # ❌ stranger
            customer.get_wallet().set_balance(
                customer.get_wallet().get_balance() - amount)      # ❌ stranger
            return "PAID"
        return "DECLINED"


# ==============================================================================
# 🛠️ STEP 2: YOUR SOLUTION AREA
# ==============================================================================
class Wallet:
    """
    [TODO]:
      - __init__(self, balance: float)   (store it privately)
      - debit(amount) -> bool : False (and no change) if amount > balance,
                                otherwise subtract and return True
      - balance_report() -> str : f"{balance:.2f}"  (for display only)
    """
    def __init__(self, balance: float):
        self.balance = balance

    def debit(self, amount: float) -> bool:
        if self.balance - amount < 0:
            return False
        self.balance -= amount
        return True

    def balance_report(self) -> str:
        return f"{self.balance:.2f}"


class Customer:
    """
    [TODO]:
      - __init__(self, name: str, wallet: Wallet)
            Keep the wallet PRIVATE (e.g., self._wallet). There must be NO public
            `wallet` attribute and NO get_wallet() method.
      - pay(amount) -> bool : delegate to the wallet.
      - balance_report() -> str : delegate to the wallet.
    """
    def __init__(self, name: str, wallet: Wallet):
        self.name = name
        self._wallet = wallet

    def pay(self, amount: float) -> bool:
        return self._wallet.debit(amount)

    def balance_report(self) -> str:
        return self._wallet.balance_report()


class Cashier:
    """
    [TODO]: checkout(customer, amount) -> "PAID" if customer.pay(amount) else "DECLINED".
            It may call ONLY customer.pay().
    """
    def checkout(self, customer, amount: float) -> str:
        return "PAID" if customer.pay(amount) else "DECLINED"


# ==============================================================================
# 🧪 STEP 3: AUTOMATED TESTING FRAMEWORK (DO NOT CHANGE THE TEST METHODS)
# ==============================================================================
class StrictCustomer:
    """Test double: only `pay` is a friend. Touching anything else is a Demeter violation."""
    def __init__(self, will_succeed: bool):
        self.will_succeed = will_succeed
        self.pay_calls = []

    def pay(self, amount: float) -> bool:
        self.pay_calls.append(amount)
        return self.will_succeed

    def __getattr__(self, name):
        raise AssertionError(f"Law of Demeter violated: Cashier touched '{name}'")


class TestLawOfDemeterPatterns(unittest.TestCase):

    def test_wallet_debit_rules(self):
        w = Wallet(50.0)
        self.assertTrue(w.debit(20.0))
        self.assertEqual(w.balance_report(), "30.00")
        self.assertFalse(w.debit(31.0))
        self.assertEqual(w.balance_report(), "30.00")

    def test_customer_delegates_to_wallet(self):
        c = Customer("Ada", Wallet(50.0))
        self.assertTrue(c.pay(10.0))
        self.assertEqual(c.balance_report(), "40.00")
        self.assertFalse(c.pay(100.0))

    def test_customer_does_not_leak_wallet(self):
        c = Customer("Ada", Wallet(50.0))
        self.assertFalse(hasattr(c, "wallet"))
        self.assertFalse(hasattr(c, "get_wallet"))

    def test_cashier_only_uses_pay_on_success(self):
        spy = StrictCustomer(will_succeed=True)
        self.assertEqual(Cashier().checkout(spy, 12.5), "PAID")
        self.assertEqual(spy.pay_calls, [12.5])

    def test_cashier_only_uses_pay_on_failure(self):
        spy = StrictCustomer(will_succeed=False)
        self.assertEqual(Cashier().checkout(spy, 99.0), "DECLINED")
        self.assertEqual(spy.pay_calls, [99.0])

    def test_end_to_end(self):
        ada = Customer("Ada", Wallet(30.0))
        cashier = Cashier()
        self.assertEqual(cashier.checkout(ada, 20.0), "PAID")
        self.assertEqual(cashier.checkout(ada, 20.0), "DECLINED")


if __name__ == "__main__":
    print("--- Initiating Automated Code Validation Tests ---")
    unittest.main()
