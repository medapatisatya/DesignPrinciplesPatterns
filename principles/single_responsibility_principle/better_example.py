"""
================================================================================
1. BAD CODE: THE REGISTRATION GOD-CLASS
================================================================================
CRITIQUE: UserManager validates, hashes, stores, emails, and logs. Any of
five teams can break signup by editing it.
"""
import hashlib

class BadUserManager:
    def __init__(self):
        self.users = {}

    def register(self, email: str, password: str) -> bool:
        if "@" not in email or len(password) < 8:               # validation rules
            return False
        hashed = hashlib.sha256(password.encode()).hexdigest()  # security policy
        self.users[email] = hashed                              # persistence
        print(f"[SMTP] Welcome {email}!")                       # notification
        print(f"[LOG] registered {email}")                      # logging
        return True


"""
================================================================================
2. THE PRINCIPLE: "A CLASS SHOULD HAVE ONLY ONE REASON TO CHANGE"
================================================================================
Reasons to change hiding in BadUserManager:
    * Product changes validation rules.
    * Security changes the hashing algorithm.
    * Platform changes the database.
    * Marketing changes the welcome email.
Each deserves its own class. A thin service coordinates them; its single reason
to change is the registration WORKFLOW itself.
"""


"""
================================================================================
3. GOOD CODE: SMALL COLLABORATORS + A THIN ORCHESTRATOR
================================================================================
"""
import hashlib
import os
from typing import Dict, Optional

# ------------------------------------------------------------------------------
# APPROACH A: ONE CLASS PER RESPONSIBILITY
# ------------------------------------------------------------------------------

class RegistrationValidator:
    def is_valid(self, email: str, password: str) -> bool:
        return "@" in email and len(password) >= 8


class PasswordHasher:
    def hash(self, password: str, salt: Optional[bytes] = None) -> str:
        salt = salt or os.urandom(8)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
        return salt.hex() + ":" + digest.hex()

    def verify(self, password: str, stored: str) -> bool:
        salt_hex, _ = stored.split(":")
        return self.hash(password, bytes.fromhex(salt_hex)) == stored


class UserRepository:
    def __init__(self):
        self._users: Dict[str, str] = {}
    def exists(self, email: str) -> bool:
        return email in self._users
    def add(self, email: str, password_hash: str) -> None:
        self._users[email] = password_hash


class WelcomeMailer:
    def send_welcome(self, email: str) -> None:
        print(f"[SMTP] Welcome {email}!")


class RegistrationService:
    """Coordinates the workflow. Contains no validation/hashing/storage/email details."""
    def __init__(self, validator: RegistrationValidator, hasher: PasswordHasher,
                 repo: UserRepository, mailer: WelcomeMailer):
        self._validator, self._hasher = validator, hasher
        self._repo, self._mailer = repo, mailer

    def register(self, email: str, password: str) -> bool:
        if not self._validator.is_valid(email, password) or self._repo.exists(email):
            return False
        self._repo.add(email, self._hasher.hash(password))
        self._mailer.send_welcome(email)
        return True


# ------------------------------------------------------------------------------
# APPROACH B: FUNCTION-BASED RESPONSIBILITIES
# ------------------------------------------------------------------------------

def is_valid_signup(email: str, password: str) -> bool:
    return "@" in email and len(password) >= 8

def register_user(email: str, password: str, store: dict, hash_fn, notify_fn) -> bool:
    if not is_valid_signup(email, password) or email in store:
        return False
    store[email] = hash_fn(password)
    notify_fn(email)
    return True


"""
================================================================================
4. WHAT IT SOLVES IN REALITY: MONETARY AND PRODUCTION BREAKDOWN
================================================================================

PROBLEM 1: SECURITY UPGRADE WITHOUT SIGNUP RISK
-----------------------------------------------
- THE MESSY REALITY: Security mandates moving off bare SHA-256 to a salted, slow hash. In the
  god-class, that edit sits next to email and DB code, and any mistake blocks all signups.
- THE SOLUTION: Only PasswordHasher changes (as shown: salted PBKDF2). Other classes can't be
  affected.

PROBLEM 2: FOCUSED CODE REVIEW
------------------------------
- THE MESSY REALITY: Reviewers must understand five concerns to approve a one-line change.
- THE SOLUTION: A diff in WelcomeMailer needs only email expertise.

PROBLEM 3: TARGETED UNIT TESTS
------------------------------
- THE MESSY REALITY: Testing the "password >= 8 chars" rule requires a database and a mail
  server.
- THE SOLUTION: RegistrationValidator().is_valid("a@b.c", "short") needs nothing.

PROBLEM 4: PARALLEL DEVELOPMENT
-------------------------------
- THE MESSY REALITY: Four developers touch the same class on the same sprint.
- THE SOLUTION: Four files, four owners, no conflicts.
"""

if __name__ == "__main__":
    service = RegistrationService(RegistrationValidator(), PasswordHasher(),
                                  UserRepository(), WelcomeMailer())
    print("Register Ada     :", service.register("ada@example.com", "s3cretpass"))
    print("Register Ada again:", service.register("ada@example.com", "s3cretpass"))
    print("Weak password    :", service.register("bob@example.com", "123"))

    print("\n--- Function-based ---")
    store = {}
    print(register_user("x@y.com", "longenough", store, PasswordHasher().hash,
                        lambda e: print(f"[notify] {e}")))
