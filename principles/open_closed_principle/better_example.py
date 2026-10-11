"""
================================================================================
1. BAD CODE: THE FRAUD ENGINE THAT HARDCODES EVERY RULE
================================================================================
CRITIQUE: Every new fraud signal requires editing the engine at the heart of
the payment flow, the last place you want unreviewed changes.
"""

class BadFraudEngine:
    def evaluate(self, tx: dict) -> str:
        score = 0
        if tx["amount"] > 5000:
            score += 50
        if tx["country"] != "US":
            score += 30
        if tx["account_age_days"] < 7:
            score += 25
        # ❌ Next: velocity checks, device fingerprint, IP reputation...
        return "REVIEW" if score >= 70 else "APPROVE"


"""
================================================================================
2. THE PRINCIPLE: "OPEN FOR EXTENSION, CLOSED FOR MODIFICATION"
================================================================================
What Varies:
    The individual fraud signals. Risk analysts invent new ones constantly.

What Stays Stable:
    The process: ask every rule for a score, sum, compare with a threshold.
"""


"""
================================================================================
3. GOOD CODE: A RULE INTERFACE + A CLOSED ENGINE
================================================================================
"""
from abc import ABC, abstractmethod
from typing import List

# ------------------------------------------------------------------------------
# APPROACH A: CLASS-BASED RULES
# ------------------------------------------------------------------------------

class FraudRule(ABC):
    @abstractmethod
    def score(self, tx: dict) -> int: ...


class HighAmountRule(FraudRule):
    def score(self, tx: dict) -> int:
        return 50 if tx["amount"] > 5000 else 0

class ForeignCountryRule(FraudRule):
    def __init__(self, home_country: str = "US"):
        self._home = home_country
    def score(self, tx: dict) -> int:
        return 30 if tx["country"] != self._home else 0

class NewAccountRule(FraudRule):
    def score(self, tx: dict) -> int:
        return 25 if tx["account_age_days"] < 7 else 0


class FraudEngine:
    """CLOSED for modification. Adding a rule = passing/registering another FraudRule."""
    REVIEW_THRESHOLD = 70

    def __init__(self, rules: List[FraudRule]):
        self._rules = list(rules)

    def register(self, rule: FraudRule) -> None:
        self._rules.append(rule)

    def total_score(self, tx: dict) -> int:
        return sum(rule.score(tx) for rule in self._rules)

    def evaluate(self, tx: dict) -> str:
        return "REVIEW" if self.total_score(tx) >= self.REVIEW_THRESHOLD else "APPROVE"


# --- EXTENSION (a new file written by the risk team; the engine is untouched) ---
class VelocityRule(FraudRule):
    def score(self, tx: dict) -> int:
        return 40 if tx.get("tx_last_hour", 0) > 5 else 0


# ------------------------------------------------------------------------------
# APPROACH B: FUNCTION-BASED RULES (each rule is just a callable)
# ------------------------------------------------------------------------------

def high_amount(tx: dict) -> int: return 50 if tx["amount"] > 5000 else 0
def new_account(tx: dict) -> int: return 25 if tx["account_age_days"] < 7 else 0

def evaluate_with_functions(tx: dict, rules, threshold: int = 70) -> str:
    return "REVIEW" if sum(rule(tx) for rule in rules) >= threshold else "APPROVE"


"""
================================================================================
4. WHAT IT SOLVES IN REALITY: MONETARY AND PRODUCTION BREAKDOWN
================================================================================

PROBLEM 1: EMERGENCY RULES DURING AN ATTACK
-------------------------------------------
- THE MESSY REALITY: A card-testing attack starts. You need a velocity rule NOW. Editing the
  core engine at 2 AM risks blocking all legitimate payments.
- THE SOLUTION: Ship VelocityRule as a new, isolated class and register it. The engine's
  code and tests are unchanged.

PROBLEM 2: AUDITABILITY
-----------------------
- THE MESSY REALITY: Compliance asks "what changed in the engine last quarter?" and gets a
  diff full of unrelated rule edits.
- THE SOLUTION: The engine's history is empty; each rule has its own reviewable file.

PROBLEM 3: A/B TESTING RULES
----------------------------
- THE MESSY REALITY: You'd like to test a stricter threshold on 5% of traffic, but the rules
  are fused into one function.
- THE SOLUTION: Build two FraudEngine instances with different rule sets.

PROBLEM 4: RULE OWNERSHIP
-------------------------
- THE MESSY REALITY: Analysts can't add rules without engineers editing the core.
- THE SOLUTION: Analysts own their rule classes; engineering owns the (stable) engine.
"""

if __name__ == "__main__":
    tx = {"amount": 100, "country": "BR", "account_age_days": 3, "tx_last_hour": 9}

    engine = FraudEngine([HighAmountRule(), ForeignCountryRule(), NewAccountRule()])
    print("Before velocity rule:", engine.total_score(tx), engine.evaluate(tx))

    engine.register(VelocityRule())     # extension: engine untouched
    print("After velocity rule :", engine.total_score(tx), engine.evaluate(tx))

    print("Functional:", evaluate_with_functions(tx, [high_amount, new_account]))
