"""
================================================================================
1. BAD CODE: HIGH-LEVEL LOGIC BUILT ON A LOW-LEVEL CLASS (THE RUSHED MVP)
================================================================================
The high-level policy ("send a reset link") creates and depends on a
low-level detail (SMTP).
"""

class SmtpEmailSender:
    def send_smtp(self, to: str, body: str) -> None:
        print(f"[SMTP] To: {to} | {body}")


class BadPasswordReset:
    def __init__(self):
        self.sender = SmtpEmailSender()    # ❌ Depends on a concrete class it also constructs

    def reset(self, email: str) -> None:
        self.sender.send_smtp(email, "Click here to reset your password")


"""
================================================================================
2. THE PRINCIPLE: "DEPEND ON ABSTRACTIONS, NOT CONCRETE CLASSES"
================================================================================
Core Definition:
    (1) High-level modules should not depend on low-level modules. Both should
        depend on abstractions.
    (2) Abstractions should not depend on details; details depend on
        abstractions.

The Golden Rule:
    If a business-logic class contains `SomethingConcrete()` in its constructor
    or imports a vendor class, invert it: define the interface the BUSINESS
    needs, and make the vendor code implement it.
"""


"""
================================================================================
3. GOOD CODE: INJECT ABSTRACTIONS
================================================================================
"""
from abc import ABC, abstractmethod
from typing import Callable

# ------------------------------------------------------------------------------
# APPROACH A: CLASS-BASED ABSTRACTION (constructor injection)
# ------------------------------------------------------------------------------

class MessageSender(ABC):
    """Owned by the high-level module: describes what the BUSINESS needs."""
    @abstractmethod
    def send(self, to: str, body: str) -> None: ...


class SmtpSender(MessageSender):
    def send(self, to: str, body: str) -> None:
        print(f"[SMTP] To: {to} | {body}")

class SmsSender(MessageSender):
    def send(self, to: str, body: str) -> None:
        print(f"[SMS] To: {to} | {body}")


class PasswordReset:
    def __init__(self, sender: MessageSender):
        self._sender = sender

    def reset(self, contact: str) -> None:
        self._sender.send(contact, "Click here to reset your password")


# ------------------------------------------------------------------------------
# APPROACH B: INJECT A CALLABLE (lightest-weight abstraction in Python)
# ------------------------------------------------------------------------------

class FunctionalPasswordReset:
    def __init__(self, send: Callable[[str, str], None]):
        self._send = send

    def reset(self, contact: str) -> None:
        self._send(contact, "Click here to reset your password")


"""
================================================================================
4. WHAT IT SOLVES IN REALITY: UNABRIDGED PRODUCTION BREAKDOWN
================================================================================

PROBLEM 1: SWAPPING VENDORS
---------------------------
- THE MESSY REALITY: Your SMTP provider raises prices, or you need SMS for 2FA. BadPasswordReset
  must be edited and retested.
- THE SOLUTION: Pass SmsSender() instead. PasswordReset is untouched.

PROBLEM 2: TESTS THAT SEND REAL EMAILS
--------------------------------------
- THE MESSY REALITY: The constructor builds a real SMTP client, so a unit test either spams
  users or needs heavy monkey-patching.
- THE SOLUTION: Inject a recorder object or lambda.

PROBLEM 3: DEPENDENCY DIRECTION
-------------------------------
- THE MESSY REALITY: Policy code imports infrastructure code, so a change in infra ripples up
  into business rules.
- THE SOLUTION: Infra imports (implements) the business-owned interface. The arrow is flipped.

PROBLEM 4: ENVIRONMENT-SPECIFIC WIRING
--------------------------------------
- THE MESSY REALITY: Dev should print to console, staging should use a sandbox, prod should
  use the real thing, via scattered if ENV == ... checks.
- THE SOLUTION: Choose the implementation once, at the program's entry point.
"""

if __name__ == "__main__":
    print("--- Class-Based DIP ---")
    PasswordReset(SmtpSender()).reset("ada@example.com")
    PasswordReset(SmsSender()).reset("+15550199")

    print("\n--- Callable DIP ---")
    sent = []
    FunctionalPasswordReset(lambda to, body: sent.append((to, body))).reset("test@x.com")
    print("Captured in test:", sent)
