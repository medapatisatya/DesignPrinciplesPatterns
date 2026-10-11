"""
================================================================================
1. BAD CODE: THE INHERITANCE TREE (THE RUSHED MVP)
================================================================================
Behavior is shared by inheriting it from a parent class. Every new kind of
Duck forces us to override (or disable) behavior that doesn't apply.
"""

class BadDuck:
    def __init__(self, name: str):
        self.name = name

    def quack(self) -> str:
        return f"{self.name}: Quack!"

    def fly(self) -> str:
        return f"{self.name}: flapping wings"


class BadRubberDuck(BadDuck):
    # ❌ CRITICAL ERROR: Inherited a fly() it can't honour, so we fake it.
    def fly(self) -> str:
        return f"{self.name}: ...(does nothing)"

    def quack(self) -> str:
        return f"{self.name}: Squeak!"


class BadDecoyDuck(BadDuck):
    # ❌ Overriding to "turn off" behavior is a code smell: the hierarchy is lying.
    def fly(self) -> str:
        return f"{self.name}: ...(does nothing)"

    def quack(self) -> str:
        return f"{self.name}: ...(silence)"


"""
================================================================================
2. THE PRINCIPLE: "FAVOR COMPOSITION OVER INHERITANCE"
================================================================================
Core Definition:
    Build objects by HAVING behaviors (composition: "has-a") instead of
    INHERITING them (inheritance: "is-a").

The Golden Rule:
    If a subclass overrides a method only to disable it, or if you need a new
    subclass for every combination of features, switch to composition.
    Behaviors become pluggable parts that can be swapped, even at runtime.
"""


"""
================================================================================
3. GOOD CODE: BEHAVIORS ARE COMPOSED, NOT INHERITED
================================================================================
"""
from abc import ABC, abstractmethod
from typing import Callable

# ------------------------------------------------------------------------------
# APPROACH A: CLASS-BASED COMPOSITION (Best for behaviors that carry state)
# ------------------------------------------------------------------------------

class FlyBehavior(ABC):
    @abstractmethod
    def fly(self) -> str: ...

class FlyWithWings(FlyBehavior):
    def fly(self) -> str: return "flapping wings"

class NoFly(FlyBehavior):
    def fly(self) -> str: return "staying on the ground"

class RocketFly(FlyBehavior):
    def fly(self) -> str: return "blasting off with a rocket"


class QuackBehavior(ABC):
    @abstractmethod
    def quack(self) -> str: ...

class LoudQuack(QuackBehavior):
    def quack(self) -> str: return "Quack!"

class Squeak(QuackBehavior):
    def quack(self) -> str: return "Squeak!"

class Silent(QuackBehavior):
    def quack(self) -> str: return "..."


class Duck:
    """One concrete class. Variety comes from the parts we plug in."""
    def __init__(self, name: str, fly_behavior: FlyBehavior, quack_behavior: QuackBehavior):
        self.name = name
        self._fly_behavior = fly_behavior
        self._quack_behavior = quack_behavior

    def perform_fly(self) -> str:
        return f"{self.name}: {self._fly_behavior.fly()}"

    def perform_quack(self) -> str:
        return f"{self.name}: {self._quack_behavior.quack()}"

    def set_fly_behavior(self, fly_behavior: FlyBehavior) -> None:
        self._fly_behavior = fly_behavior  # Runtime swap: impossible with inheritance


# ------------------------------------------------------------------------------
# APPROACH B: FUNCTION-BASED COMPOSITION (Best for simple, stateless behaviors)
# ------------------------------------------------------------------------------

def fly_with_wings() -> str: return "flapping wings"
def no_fly() -> str: return "staying on the ground"
def loud_quack() -> str: return "Quack!"
def squeak() -> str: return "Squeak!"

class FunctionalDuck:
    def __init__(self, name: str,
                 fly: Callable[[], str] = fly_with_wings,
                 quack: Callable[[], str] = loud_quack):
        self.name = name
        self.fly = fly
        self.quack = quack

    def describe(self) -> str:
        return f"{self.name}: {self.fly()} / {self.quack()}"


"""
================================================================================
4. WHAT IT SOLVES IN REALITY: UNABRIDGED PRODUCTION BREAKDOWN
================================================================================

PROBLEM 1: CLASS EXPLOSION
--------------------------
- THE MESSY REALITY: Marketing wants ducks that fly+squeak, fly+silent, walk+quack,
  rocket+squeak... With inheritance, every combination is a new subclass. 3 fly styles
  x 3 quack styles = 9 classes, and it grows multiplicatively.
- THE SOLUTION: 3 + 3 small behavior classes, combined freely at construction time.

PROBLEM 2: BEHAVIOR THAT CAN'T CHANGE AT RUNTIME
------------------------------------------------
- THE MESSY REALITY: A duck gets a rocket booster mid-game. Inheritance fixes behavior
  at class-definition time; you can't turn a 'Duck' into a 'RocketDuck' on the fly.
- THE SOLUTION: duck.set_fly_behavior(RocketFly()). One line, no new class.

PROBLEM 3: THE "FAKE OVERRIDE" LIE
----------------------------------
- THE MESSY REALITY: BadRubberDuck inherits fly() and pretends. Any caller that trusts
  the parent's contract now gets surprising behavior.
- THE SOLUTION: A rubber duck simply composes NoFly. Nothing is inherited that
  shouldn't be.

PROBLEM 4: REUSE ACROSS UNRELATED CLASSES
-----------------------------------------
- THE MESSY REALITY: A Drone also needs 'flap wings' or 'rocket' flight, but a Drone
  is not a Duck. You can't inherit from Duck without absurdity.
- THE SOLUTION: Drone(fly_behavior=RocketFly()). Behaviors live outside any hierarchy.
"""

if __name__ == "__main__":
    print("--- Bad Inheritance ---")
    print(BadRubberDuck("Rubby").fly())

    print("\n--- Class-Based Composition ---")
    mallard = Duck("Mallard", FlyWithWings(), LoudQuack())
    rubber = Duck("Rubber", NoFly(), Squeak())
    print(mallard.perform_fly())
    print(rubber.perform_quack())
    print("Rubber duck gets a rocket booster...")
    rubber.set_fly_behavior(RocketFly())
    print(rubber.perform_fly())

    print("\n--- Function-Based Composition ---")
    print(FunctionalDuck("Decoy", fly=no_fly, quack=squeak).describe())
