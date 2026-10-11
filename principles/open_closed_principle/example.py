"""
================================================================================
1. BAD CODE: THE IF/ELIF DISCOUNT LADDER (THE RUSHED MVP)
================================================================================
Every new customer type forces us to MODIFY this tested, deployed method.
"""

class BadDiscountCalculator:
    def apply(self, price: float, customer_type: str) -> float:
        # ❌ CRITICAL ERROR: Closed to extension, open to modification (the reverse of OCP).
        if customer_type == "regular":
            return price
        elif customer_type == "vip":
            return price * 0.90
        elif customer_type == "employee":
            return price * 0.70
        else:
            raise ValueError(f"Unknown customer type: {customer_type}")


"""
================================================================================
2. THE PRINCIPLE: "OPEN FOR EXTENSION, CLOSED FOR MODIFICATION"
================================================================================
Core Definition:
    You should be able to add NEW behavior by writing NEW code, without editing
    code that already works.

The Golden Rule:
    If adding a feature means editing an existing if/elif chain or switch, the
    class is not closed. Define an abstraction, then extend by adding
    implementations.
"""


"""
================================================================================
3. GOOD CODE: NEW RULES ARE ADDED, NEVER EDITED IN
================================================================================
"""
from abc import ABC, abstractmethod
from typing import Callable, Dict

# ------------------------------------------------------------------------------
# APPROACH A: CLASS-BASED EXTENSION
# ------------------------------------------------------------------------------

class DiscountRule(ABC):
    @abstractmethod
    def apply(self, price: float) -> float: ...

class RegularDiscount(DiscountRule):
    def apply(self, price: float) -> float: return price

class VipDiscount(DiscountRule):
    def apply(self, price: float) -> float: return price * 0.90

class EmployeeDiscount(DiscountRule):
    def apply(self, price: float) -> float: return price * 0.70


class DiscountCalculator:
    """CLOSED: this class never changes when a new rule appears."""
    def __init__(self):
        self._rules: Dict[str, DiscountRule] = {}

    def register(self, customer_type: str, rule: DiscountRule) -> None:
        self._rules[customer_type] = rule

    def apply(self, price: float, customer_type: str) -> float:
        try:
            return self._rules[customer_type].apply(price)
        except KeyError:
            raise ValueError(f"Unknown customer type: {customer_type}")


# --- EXTENSION: imagine this lives in a brand-new file added next week ---------
class BlackFridayDiscount(DiscountRule):
    def apply(self, price: float) -> float: return price * 0.50


# ------------------------------------------------------------------------------
# APPROACH B: FUNCTION REGISTRY WITH A DECORATOR
# ------------------------------------------------------------------------------

DISCOUNTS: Dict[str, Callable[[float], float]] = {}

def discount(name: str):
    def decorator(fn: Callable[[float], float]):
        DISCOUNTS[name] = fn
        return fn
    return decorator

@discount("regular")
def regular(price: float) -> float: return price

@discount("vip")
def vip(price: float) -> float: return price * 0.90

@discount("student")   # Extension = just another decorated function
def student(price: float) -> float: return price * 0.80

def apply_discount(price: float, customer_type: str) -> float:
    return DISCOUNTS[customer_type](price)   # CLOSED: never edited


"""
================================================================================
4. WHAT IT SOLVES IN REALITY: UNABRIDGED PRODUCTION BREAKDOWN
================================================================================

PROBLEM 1: REGRESSION IN WORKING CODE
-------------------------------------
- THE MESSY REALITY: Adding "student" means editing the ladder. One mistyped multiplier or
  accidentally deleted elif and VIP pricing is wrong in production.
- THE SOLUTION: Existing classes are never touched, so they can't regress.

PROBLEM 2: RE-TESTING EVERYTHING
--------------------------------
- THE MESSY REALITY: Any edit to BadDiscountCalculator forces QA to re-verify every branch.
- THE SOLUTION: Only the new rule needs new tests. The proven code stays proven.

PROBLEM 3: SHIPPING AS A PLUGIN
-------------------------------
- THE MESSY REALITY: A partner team wants to ship its own discount type but would need
  commit rights to your core file.
- THE SOLUTION: They write a DiscountRule in their repo and register() it.

PROBLEM 4: TIME-BOXED CAMPAIGNS
-------------------------------
- THE MESSY REALITY: Black Friday logic must be added, then removed on Monday: two risky
  edits to core code.
- THE SOLUTION: register() it Friday, drop the registration Monday.
"""

if __name__ == "__main__":
    print("--- Class-Based OCP ---")
    calc = DiscountCalculator()
    calc.register("regular", RegularDiscount())
    calc.register("vip", VipDiscount())
    print("VIP:", calc.apply(100.0, "vip"))
    calc.register("black_friday", BlackFridayDiscount())   # extension, no edits
    print("Black Friday:", calc.apply(100.0, "black_friday"))

    print("\n--- Function Registry OCP ---")
    print("Student:", apply_discount(100.0, "student"))
