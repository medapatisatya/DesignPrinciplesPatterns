"""
================================================================================
1. BAD CODE: THE USER-TYPE INHERITANCE EXPLOSION (THE MAINTENANCE TRAP)
================================================================================
A SaaS app models "who the user is" through subclasses. Roles (admin/member)
and billing plans (free/pro) are two independent axes, but inheritance can only
express one axis at a time.

CRITIQUE: Every new role or plan multiplies the number of classes.
"""

class BadUser:
    def can_delete_projects(self) -> bool: return False
    def project_limit(self) -> int: return 3

class BadAdminUser(BadUser):
    def can_delete_projects(self) -> bool: return True

class BadProUser(BadUser):
    def project_limit(self) -> int: return 50

class BadProAdminUser(BadAdminUser):
    # ❌ Duplicated: copy-pasted Pro logic because we can't inherit from two trees cleanly
    def project_limit(self) -> int: return 50

# Next quarter: "Enterprise plan" and "Billing Manager" role => 3 plans x 3 roles = 9 classes.
# And a Pro user who upgrades to Enterprise? You can't change an object's class cleanly.


"""
================================================================================
2. THE PRINCIPLE: "FAVOR COMPOSITION OVER INHERITANCE"
================================================================================
What Varies:
    The user's ROLE (permissions) and PLAN (limits). They vary independently.

What Stays Stable:
    An Account that answers: "Can this user do X?" and "How many projects can
    they create?"
"""


"""
================================================================================
3. GOOD CODE: ACCOUNT = ROLE + PLAN (COMPOSED, SWAPPABLE)
================================================================================
"""
from abc import ABC, abstractmethod
from typing import FrozenSet

# ------------------------------------------------------------------------------
# APPROACH A: CLASS-BASED COMPOSITION
# ------------------------------------------------------------------------------

class Role(ABC):
    @abstractmethod
    def permissions(self) -> FrozenSet[str]: ...

class MemberRole(Role):
    def permissions(self) -> FrozenSet[str]:
        return frozenset({"read", "write"})

class AdminRole(Role):
    def permissions(self) -> FrozenSet[str]:
        return frozenset({"read", "write", "delete", "manage_users"})


class Plan(ABC):
    @abstractmethod
    def project_limit(self) -> int: ...

class FreePlan(Plan):
    def project_limit(self) -> int: return 3

class ProPlan(Plan):
    def project_limit(self) -> int: return 50

class EnterprisePlan(Plan):
    def project_limit(self) -> int: return 10_000


class Account:
    """Single class. Never needs a subclass for a new role/plan combination."""
    def __init__(self, email: str, role: Role, plan: Plan):
        self.email = email
        self._role = role
        self._plan = plan

    def can(self, action: str) -> bool:
        return action in self._role.permissions()

    def project_limit(self) -> int:
        return self._plan.project_limit()

    def upgrade_plan(self, new_plan: Plan) -> None:
        self._plan = new_plan  # Runtime change: no migration of object types

    def change_role(self, new_role: Role) -> None:
        self._role = new_role


# ------------------------------------------------------------------------------
# APPROACH B: FUNCTION/DATA-BASED COMPOSITION (stateless rules as plain data)
# ------------------------------------------------------------------------------

ROLE_PERMISSIONS = {
    "member": {"read", "write"},
    "admin": {"read", "write", "delete", "manage_users"},
}
PLAN_LIMITS = {"free": 3, "pro": 50, "enterprise": 10_000}

class LightweightAccount:
    def __init__(self, email: str, role: str, plan: str):
        self.email, self.role, self.plan = email, role, plan

    def can(self, action: str) -> bool:
        return action in ROLE_PERMISSIONS[self.role]

    def project_limit(self) -> int:
        return PLAN_LIMITS[self.plan]


"""
================================================================================
4. WHAT IT SOLVES IN REALITY: MONETARY AND PRODUCTION BREAKDOWN
================================================================================

PROBLEM 1: PLAN UPGRADES AT RUNTIME (REVENUE)
---------------------------------------------
- THE MESSY REALITY: A customer upgrades from Pro to Enterprise while logged in. With the
  inheritance tree there's no way to "become" a different class; you rebuild the object
  and risk losing session state, or deploy hacks like __class__ assignment.
- THE SOLUTION: account.upgrade_plan(EnterprisePlan()). Same object, new capability,
  immediately billable.

PROBLEM 2: ROLE x PLAN COMBINATORIAL GROWTH
-------------------------------------------
- THE MESSY REALITY: Adding a 'BillingManager' role means writing BillingManager,
  ProBillingManager, EnterpriseBillingManager... Each copy-paste is a bug waiting.
- THE SOLUTION: Add ONE Role class. It works with every existing plan automatically.

PROBLEM 3: TESTING PERMISSIONS IN ISOLATION
-------------------------------------------
- THE MESSY REALITY: To test "can an admin delete?" in the bad design you instantiate a
  whole user type tangled up with plan rules.
- THE SOLUTION: Test AdminRole().permissions() on its own, and Account with tiny fake
  roles/plans.

PROBLEM 4: A/B EXPERIMENTS AND PROMOTIONS
-----------------------------------------
- THE MESSY REALITY: Marketing runs a "Pro limits for free users for 30 days" promo.
  Inheritance needs a 'PromoFreeUser' class and a migration after 30 days.
- THE SOLUTION: Plug a PromoPlan into those accounts, then swap back to FreePlan when
  the promo ends.
"""

if __name__ == "__main__":
    print("--- Composed Account ---")
    acct = Account("ada@example.com", MemberRole(), FreePlan())
    print("Can delete?", acct.can("delete"), "| Projects:", acct.project_limit())

    print("\nPromoting to admin and upgrading plan at runtime...")
    acct.change_role(AdminRole())
    acct.upgrade_plan(EnterprisePlan())
    print("Can delete?", acct.can("delete"), "| Projects:", acct.project_limit())

    print("\n--- Lightweight (data-driven) Account ---")
    light = LightweightAccount("linus@example.com", "admin", "pro")
    print("Can manage users?", light.can("manage_users"), "| Projects:", light.project_limit())
