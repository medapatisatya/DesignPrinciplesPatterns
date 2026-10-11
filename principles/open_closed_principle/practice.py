"""
================================================================================
CHALLENGE: OPEN-CLOSED PRINCIPLE (CLEAN SLATE)
================================================================================
PROBLEM CONTEXT:
An e-commerce checkout applies pricing rules (percentage off, flat off, ...).
Marketing invents new promotions every month (Buy-2-Get-1, loyalty bonus...).

THE GOAL:
PriceCalculator must be CLOSED for modification. New promotions are new
PricingRule classes only.

YOUR MISSION:
1. Implement PercentageOff and FlatOff.
2. Implement PriceCalculator that applies rules in order.
3. Make all tests pass (one test defines a brand-new rule!).
"""

import unittest
from abc import ABC, abstractmethod
from typing import List, Optional

# ==============================================================================
# 🚨 STEP 1: THE BAD CODE (DO NOT USE THIS LOGIC)
# ==============================================================================
class BadPriceCalculator:
    def total(self, price: float, promo: str, value: float) -> float:
        if promo == "percent":
            return price * (1 - value / 100)
        elif promo == "flat":
            return max(price - value, 0)
        raise ValueError(promo)       # ❌ every new promo edits this method


# ==============================================================================
# 🛠️ STEP 2: YOUR SOLUTION AREA
# ==============================================================================
class PricingRule(ABC):
    @abstractmethod
    def apply(self, price: float) -> float:
        """Return the new price after this rule."""


class PercentageOff(PricingRule):
    def __init__(self, percent):
        self.percent = percent

    def apply(self, price: float) -> float:
        return price * (1 - self.percent/100)



class FlatOff(PricingRule):
    def __init__(self, amount):
            self.amount = amount
    
    def apply(self, price: float) -> float:
        final_amount = price - self.amount
        if final_amount < 0:
            final_amount = 0
        return final_amount

class PriceCalculator:
    """
    [TODO]:
      - __init__(self, rules: Optional[List[PricingRule]] = None)
      - add_rule(rule)
      - total(price) -> applies every rule IN ORDER, returns the final price
    """
    def __init__(self, rules: Optional[List[PricingRule]] = None):
        if rules:
            self.rules = rules
        else:
            self.rules = []

    def add_rule(self, rule: PricingRule) -> None:
        self.rules.append(rule)

    def total(self, price: float) -> float:
        amount = price
        for rule in self.rules:
            amount = rule.apply(amount)
        return amount


# ==============================================================================
# 🧪 STEP 3: AUTOMATED TESTING FRAMEWORK (DO NOT CHANGE THE TEST METHODS)
# ==============================================================================
class TestOpenClosedPatterns(unittest.TestCase):

    def test_no_rules_means_no_change(self):
        self.assertAlmostEqual(PriceCalculator().total(200.0), 200.0)

    def test_percentage_off(self):
        self.assertAlmostEqual(PercentageOff(10).apply(200.0), 180.0)

    def test_flat_off_never_negative(self):
        self.assertAlmostEqual(FlatOff(50).apply(30.0), 0.0)
        self.assertAlmostEqual(FlatOff(5).apply(30.0), 25.0)

    def test_rules_are_applied_in_order(self):
        calc = PriceCalculator([PercentageOff(10), FlatOff(20)])
        self.assertAlmostEqual(calc.total(200.0), 160.0)   # 200 -> 180 -> 160
        calc2 = PriceCalculator([FlatOff(20), PercentageOff(10)])
        self.assertAlmostEqual(calc2.total(200.0), 162.0)  # 200 -> 180 -> 162

    def test_add_rule_after_construction(self):
        calc = PriceCalculator()
        calc.add_rule(PercentageOff(50))
        self.assertAlmostEqual(calc.total(80.0), 40.0)

    def test_brand_new_rule_requires_no_modification(self):
        class LoyaltyBonus(PricingRule):          # a promo invented AFTER the calculator
            def apply(self, price: float) -> float:
                return price - 1.0
        calc = PriceCalculator([PercentageOff(10), LoyaltyBonus()])
        self.assertAlmostEqual(calc.total(100.0), 89.0)

    def test_calculators_do_not_share_rules(self):
        a, b = PriceCalculator(), PriceCalculator()
        a.add_rule(FlatOff(10))
        self.assertAlmostEqual(b.total(100.0), 100.0)


if __name__ == "__main__":
    print("--- Initiating Automated Code Validation Tests ---")
    unittest.main()
