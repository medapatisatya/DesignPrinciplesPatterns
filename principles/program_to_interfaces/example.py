"""
================================================================================
1. BAD CODE: PROGRAMMING TO CONCRETE CLASSES (THE RUSHED MVP)
================================================================================
The ZooKeeper knows every concrete animal class and branches on type.
"""

class Dog:
    def bark(self) -> str: return "Woof!"

class Cat:
    def meow(self) -> str: return "Meow!"


class BadZooKeeper:
    def make_noise(self, animal) -> str:
        # ❌ CRITICAL ERROR: Knowledge of every concrete type + differing method names.
        if isinstance(animal, Dog):
            return animal.bark()
        elif isinstance(animal, Cat):
            return animal.meow()
        else:
            raise TypeError(f"Don't know how to handle {type(animal).__name__}")


"""
================================================================================
2. THE PRINCIPLE: "PROGRAM TO INTERFACES, NOT IMPLEMENTATIONS"
================================================================================
Core Definition:
    Write code against a contract (abstract class, Protocol, or agreed method
    shape), never against a specific concrete class.

The Golden Rule:
    If client code contains isinstance() ladders or imports a concrete class just
    to call it, the client is welded to implementation details. Depend on what an
    object CAN DO, not what it IS.
"""


"""
================================================================================
3. GOOD CODE: CLIENTS TALK TO A CONTRACT
================================================================================
"""
from abc import ABC, abstractmethod
from typing import Iterable, Protocol

# ------------------------------------------------------------------------------
# APPROACH A: ABSTRACT BASE CLASS (explicit, enforced contract)
# ------------------------------------------------------------------------------

class Animal(ABC):
    @abstractmethod
    def make_sound(self) -> str: ...

class GoodDog(Animal):
    def make_sound(self) -> str: return "Woof!"

class GoodCat(Animal):
    def make_sound(self) -> str: return "Meow!"

class GoodCow(Animal):  # Added later; ZooKeeper needs ZERO changes.
    def make_sound(self) -> str: return "Moo!"


class ZooKeeper:
    def make_noise(self, animal: Animal) -> str:
        return animal.make_sound()

    def morning_chorus(self, animals: Iterable[Animal]) -> list:
        return [a.make_sound() for a in animals]


# ------------------------------------------------------------------------------
# APPROACH B: PROTOCOL (structural typing; no inheritance needed)
# ------------------------------------------------------------------------------

class SoundMaker(Protocol):
    def make_sound(self) -> str: ...

class Robot:  # Not an Animal at all, but satisfies the contract.
    def make_sound(self) -> str: return "Beep boop"

def broadcast(sources: Iterable[SoundMaker]) -> list:
    return [s.make_sound() for s in sources]


"""
================================================================================
4. WHAT IT SOLVES IN REALITY: UNABRIDGED PRODUCTION BREAKDOWN
================================================================================

PROBLEM 1: EVERY NEW TYPE REOPENS CORE CODE
-------------------------------------------
- THE MESSY REALITY: Adding a Cow means editing BadZooKeeper's isinstance ladder, retesting
  everything it does, and hoping nobody forgot an elif elsewhere in the codebase.
- THE SOLUTION: GoodCow implements Animal. ZooKeeper is untouched.

PROBLEM 2: INCONSISTENT METHOD NAMES
------------------------------------
- THE MESSY REALITY: bark() vs meow() vs moo(): callers must memorize each class's vocabulary.
- THE SOLUTION: One method name (make_sound) defined by the interface.

PROBLEM 3: TESTING WITH STAND-INS
---------------------------------
- THE MESSY REALITY: To test ZooKeeper you need real Dog and Cat objects (and everything
  their constructors pull in).
- THE SOLUTION: Pass any tiny fake that has make_sound(). Tests become one-liners.

PROBLEM 4: THIRD-PARTY CLASSES
------------------------------
- THE MESSY REALITY: You can't make a vendor's class inherit from your base.
- THE SOLUTION: A Protocol lets any object with the right shape plug in (see Robot).
"""

if __name__ == "__main__":
    print("--- Class-Based Interface ---")
    keeper = ZooKeeper()
    print(keeper.morning_chorus([GoodDog(), GoodCat(), GoodCow()]))

    print("\n--- Protocol-Based Interface ---")
    print(broadcast([GoodDog(), Robot()]))
