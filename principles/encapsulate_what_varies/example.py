"""
================================================================================
1. BAD CODE: THE HARDCODED MONOLITH (THE RUSHED MVP)
================================================================================
In this setup, the core Order engine handles both order state and concrete 
shipping business rules simultaneously.
"""

class BadOrder:
    def __init__(self, amount: float, shipping_method: str):
        self.amount = amount
        self.shipping_method = shipping_method

    def calculate_total(self) -> float:
        # ❌ CRITICAL ERROR: WHAT VARIES IS CONFLATED WITH WHAT STAYS THE SAME.
        # This block is a magnet for code instability and team bottlenecks.
        if self.shipping_method == "standard":
            shipping_cost = 5.00
        elif self.shipping_method == "express":
            shipping_cost = 15.00
        elif self.shipping_method == "overnight":
            shipping_cost = 30.00
        else:
            shipping_cost = 0.00
            
        return self.amount + shipping_cost


"""
================================================================================
2. THE PRINCIPLE: "ENCAPSULATE WHAT VARIES"
================================================================================
Core Definition:
    Identify the aspects of your application that are highly likely to change 
    based on shifting business requirements, and separate them from the parts 
    that remain stable.

The Golden Rule:
    If you find yourself repeatedly opening the same file to add 'if/else' 
    statements or modify constants whenever management asks for a new feature, 
    that logic does not belong there. Extract it, isolate it, and hide it 
    behind a consistent boundary.
"""


"""
================================================================================
3. GOOD CODE: CLEANLY ISOLATED VARIATIONS
================================================================================
"""
from abc import ABC, abstractmethod

# ------------------------------------------------------------------------------
# APPROACH A: CLASS-BASED ENCAPSULATION (Best for complex/stateful variations)
# ------------------------------------------------------------------------------

class ShippingStrategy(ABC):
    """The Unchanging Boundary (Interface)"""
    @abstractmethod
    def calculate(self, amount: float) -> float:
        pass

class StandardShipping(ShippingStrategy):
    def calculate(self, amount: float) -> float:
        return 5.00

class ExpressShipping(ShippingStrategy):
    def calculate(self, amount: float) -> float:
        return 15.00

class OvernightShipping(ShippingStrategy):
    def calculate(self, amount: float) -> float:
        return 30.00


class ClassBasedOrder:
    def __init__(self, amount: float, shipping_strategy: ShippingStrategy):
        self.amount = amount
        self.shipping_strategy = shipping_strategy  # Dynamic dependency injection

    def calculate_total(self) -> float:
        # Core order engine is completely protected from volatile rate changes.
        return self.amount + self.shipping_strategy.calculate(self.amount)


# ------------------------------------------------------------------------------
# APPROACH B: FUNCTION-BASED ENCAPSULATION (Best for simple/stateless Python logic)
# ------------------------------------------------------------------------------

def calc_standard(amount: float) -> float: return 5.00
def calc_express(amount: float) -> float: return 15.00
def calc_overnight(amount: float) -> float: return 30.00

# Central registry acting as our structural plug-and-play map
SHIPPING_REGISTRY = {
    "standard": calc_standard,
    "express": calc_express,
    "overnight": calc_overnight
}

class FunctionBasedOrder:
    def __init__(self, amount: float, shipping_method: str):
        self.amount = amount
        self.shipping_method = shipping_method

    def calculate_total(self) -> float:
        # Gracefully defaults to a zero-cost lambda if a method isn't found
        calculator = SHIPPING_REGISTRY.get(self.shipping_method, lambda x: 0.0)
        return self.amount + calculator(self.amount)


"""
================================================================================
4. WHAT IT SOLVES IN REALITY: UNABRIDGED PRODUCTION BREAKDOWN
================================================================================

PROBLEM 1: GIT MERGE CONFLICT HELL
---------------------------------
- THE MESSY REALITY: Three developers are assigned to implement Canada Shipping, 
  Black Friday Shipping, and Local Pickup simultaneously. In the 'Bad Code', 
  all three modify the exact same if/else block in the exact same file. On merge 
  day, Git breaks, code overwrites occur, and hours are wasted resolving conflicts.
- THE SOLUTION: Developers create completely separate files containing their 
  isolated classes or functions. They merge their individual files effortlessly 
  without ever blocking or stepping on each other's code.

PROBLEM 2: THE "BLAST RADIUS" SIDE-EFFECT BUG
---------------------------------------------
- THE MESSY REALITY: A request comes in to add a surcharge to Express Shipping. 
  A developer modifies the monolithic 'BadOrder' class. While editing, they 
  accidentally introduce a typo or break an internal variable used by Standard 
  Shipping. Express works great, but Standard Shipping breaks across the site.
- THE SOLUTION: Encapsulation creates an architectural firewall. Rewriting or 
  refactoring the 'ExpressShipping' class has a blast radius of zero. It is physically 
  impossible to break Standard Shipping because its logic lives in another room.

PROBLEM 3: FLAKY, SLOW TESTING SUITES
-------------------------------------
- THE MESSY REALITY: You want to unit test your shipping calculations. In the 
  Bad Code, you must spin up a whole Order instance, mock out database entities, 
  and instantiate complex business logic states just to test a simple $5 rule. 
  Tests become slow, fragile, and prone to breaking due to outside failures.
- THE SOLUTION: You test the isolated variations directly. Testing 'calc_standard()' 
  takes less than a millisecond, requires absolutely zero mock databases, and 
  will never fail unless the math itself is fundamentally wrong.

PROBLEM 4: RIGID, 3 AM EMERGENCY DEPLOYMENTS
---------------------------------------------
- THE MESSY REALITY: A severe blizzard halts operations. Overnight shipping must 
  be disabled instantly. In the Bad Code, a developer must rewrite code, run 
  staging pipelines, and push a massive system deployment at 3 AM to avoid 
  charging customers for unfulfillable options.
- THE SOLUTION: Because logic is mapped behind a structural registry or interface, 
  the engine can dynamically fetch active strategies from a database or a configuration 
  file at runtime. The operator flips an admin toggle, swapping the algorithm 
  instantly without pushing code or restarting servers.
"""

# Execution proof-of-concept
if __name__ == "__main__":
    print("--- Running Class-Based Architecture ---")
    order_oop = ClassBasedOrder(250.0, ExpressShipping())
    print(f"Total: ${order_oop.calculate_total()}\n")

    print("--- Running Function-Based Architecture ---")
    order_func = FunctionBasedOrder(250.0, "express")
    print(f"Total: ${order_func.calculate_total()}")
