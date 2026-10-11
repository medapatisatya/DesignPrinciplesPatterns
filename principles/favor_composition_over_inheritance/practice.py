"""
================================================================================
CHALLENGE: FAVOR COMPOSITION OVER INHERITANCE (CLEAN SLATE)
================================================================================
PROBLEM CONTEXT:
You're building a game. Characters can move (walk, fly, swim) and attack
(sword, bow, magic). The designers want Elves that walk+bow, Mermaids that
swim+magic, Dragons that fly+magic... and a character who can LEARN to fly
mid-game.

THE GOAL:
Do NOT create a subclass per character type. Compose behaviors into a single
Character class so combinations are free and swappable at runtime.

YOUR MISSION:
1. Implement the concrete movement and attack behaviors.
2. Implement Character so it HAS a move behavior and an attack behavior.
3. Make all tests pass.
"""

import unittest
from abc import ABC, abstractmethod

# ==============================================================================
# 🚨 STEP 1: THE BAD CODE (DO NOT USE THIS LOGIC)
# ==============================================================================
class BadCharacter:
    def move(self): return "walking"
    def attack(self): return "slash"

class BadElf(BadCharacter):
    def attack(self): return "shoot"       # new subclass per combination...

class BadMermaid(BadCharacter):
    def move(self): return "swimming"      # ...and no way to learn new skills
    def attack(self): return "cast"


# ==============================================================================
# 🛠️ STEP 2: YOUR SOLUTION AREA
# ==============================================================================
class MoveBehavior(ABC):
    @abstractmethod
    def move(self) -> str: ...

class AttackBehavior(ABC):
    @abstractmethod
    def attack(self) -> str: ...


# [TODO]: Implement each class so that move()/attack() returns EXACTLY:
#   WalkMove -> "walking"     FlyMove -> "flying"     SwimMove -> "swimming"
#   SwordAttack -> "slash"    BowAttack -> "shoot"    MagicAttack -> "cast"
class WalkMove(MoveBehavior):
    def move(self):return "walking"
class FlyMove(MoveBehavior):
    def move(self): return "flying"
class SwimMove(MoveBehavior):
    def move(self): return "swimming"

class SwordAttack(AttackBehavior):
    def attack(self): return "slash"
class BowAttack(AttackBehavior):
    def attack(self): return "shoot"
class MagicAttack(AttackBehavior):
    def attack(self): return "cast"


class Character:
    """
    [TODO]: Compose behaviors instead of inheriting them.
      - __init__(self, name, move_behavior, attack_behavior)
      - move()   -> f"{name} is {<move result>}"      e.g. "Aria is walking"
      - attack() -> f"{name} uses {<attack result>}"   e.g. "Aria uses slash"
      - set_move_behavior(new_behavior)   (swap at runtime)
      - set_attack_behavior(new_behavior)
    """
    def __init__(self, name: str, move_behavior: MoveBehavior, attack_behavior: AttackBehavior):
        self.name = name
        self.move_behavior = move_behavior
        self.attack_behavior = attack_behavior

    def move(self) -> str:
        return f"{self.name} is {self.move_behavior.move()}"

    def attack(self) -> str:
        return f"{self.name} uses {self.attack_behavior.attack()}"

    def set_move_behavior(self, move_behavior: MoveBehavior) -> None:
        self.move_behavior = move_behavior

    def set_attack_behavior(self, attack_behavior: AttackBehavior) -> None:
        self.attack_behavior = attack_behavior


# ==============================================================================
# 🧪 STEP 3: AUTOMATED TESTING FRAMEWORK (DO NOT CHANGE THE TEST METHODS)
# ==============================================================================
class TestCompositionPatterns(unittest.TestCase):

    def test_behaviors_return_expected_strings(self):
        self.assertEqual(WalkMove().move(), "walking")
        self.assertEqual(FlyMove().move(), "flying")
        self.assertEqual(SwimMove().move(), "swimming")
        self.assertEqual(SwordAttack().attack(), "slash")
        self.assertEqual(BowAttack().attack(), "shoot")
        self.assertEqual(MagicAttack().attack(), "cast")

    def test_character_uses_composed_behaviors(self):
        elf = Character("Lyra", WalkMove(), BowAttack())
        self.assertEqual(elf.move(), "Lyra is walking")
        self.assertEqual(elf.attack(), "Lyra uses shoot")

    def test_any_combination_without_new_subclass(self):
        dragon = Character("Smaug", FlyMove(), MagicAttack())
        self.assertEqual(dragon.move(), "Smaug is flying")
        self.assertEqual(dragon.attack(), "Smaug uses cast")
        self.assertIs(type(dragon), Character)

    def test_runtime_behavior_swap(self):
        hero = Character("Aria", WalkMove(), SwordAttack())
        hero.set_move_behavior(FlyMove())
        hero.set_attack_behavior(MagicAttack())
        self.assertEqual(hero.move(), "Aria is flying")
        self.assertEqual(hero.attack(), "Aria uses cast")

    def test_new_behavior_needs_no_change_to_character(self):
        class TeleportMove(MoveBehavior):
            def move(self) -> str:
                return "teleporting"

        mage = Character("Merlin", TeleportMove(), MagicAttack())
        self.assertEqual(mage.move(), "Merlin is teleporting")

    def test_characters_do_not_share_behavior_state(self):
        a = Character("A", WalkMove(), SwordAttack())
        b = Character("B", WalkMove(), SwordAttack())
        a.set_move_behavior(SwimMove())
        self.assertEqual(b.move(), "B is walking")


if __name__ == "__main__":
    print("--- Initiating Automated Code Validation Tests ---")
    unittest.main()
