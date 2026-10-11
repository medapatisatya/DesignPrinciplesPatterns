"""
================================================================================
1. BAD CODE: THE GOD-CLASS INVOICE (THE RUSHED MVP)
================================================================================
One class calculates money, saves to storage, formats output, and emails.
It has FOUR reasons to change.
"""

class BadInvoice:
    def __init__(self, items: list):
        self.items = items   # list of (name, price)

    def calculate_total(self) -> float:           # reason 1: pricing / tax rules change
        return sum(price for _, price in self.items)

    def save(self, db: dict) -> None:             # reason 2: storage technology changes
        db["invoice"] = self.items

    def to_text(self) -> str:                     # reason 3: layout / branding changes
        lines = [f"{n}: ${p:.2f}" for n, p in self.items]
        return "\n".join(lines + [f"TOTAL: ${self.calculate_total():.2f}"])

    def email(self, address: str) -> None:        # reason 4: mail provider changes
        print(f"[SMTP] -> {address}\n{self.to_text()}")


"""
================================================================================
2. THE PRINCIPLE: "A CLASS SHOULD HAVE ONLY ONE REASON TO CHANGE" (SRP)
================================================================================
Core Definition:
    Each class should be responsible to one actor/concern, so a change in that
    concern touches only that class.

The Golden Rule:
    If you can describe a class only with "and" (calculates AND saves AND
    formats AND emails), split it. A reason to change = a stakeholder who might
    ask you to modify it.
"""


"""
================================================================================
3. GOOD CODE: ONE CLASS, ONE REASON TO CHANGE
================================================================================
"""
from dataclasses import dataclass
from typing import Dict, List, Tuple

# ------------------------------------------------------------------------------
# APPROACH A: CLASS-BASED SEPARATION
# ------------------------------------------------------------------------------

@dataclass
class Invoice:
    """Pure data holder."""
    items: List[Tuple[str, float]]


class InvoiceCalculator:               # Changes only when pricing rules change
    def total(self, invoice: Invoice) -> float:
        return sum(price for _, price in invoice.items)


class InvoiceRepository:               # Changes only when storage changes
    def __init__(self):
        self._db: Dict[str, Invoice] = {}
    def save(self, key: str, invoice: Invoice) -> None:
        self._db[key] = invoice


class InvoiceFormatter:                # Changes only when layout changes
    def to_text(self, invoice: Invoice, total: float) -> str:
        lines = [f"{n}: ${p:.2f}" for n, p in invoice.items]
        return "\n".join(lines + [f"TOTAL: ${total:.2f}"])


class InvoiceMailer:                   # Changes only when delivery changes
    def send(self, address: str, body: str) -> None:
        print(f"[SMTP] -> {address}\n{body}")


# ------------------------------------------------------------------------------
# APPROACH B: FUNCTION-BASED SEPARATION (stateless responsibilities as functions)
# ------------------------------------------------------------------------------

def calculate_total(items: List[Tuple[str, float]]) -> float:
    return sum(price for _, price in items)

def format_invoice(items: List[Tuple[str, float]], total: float) -> str:
    lines = [f"{n}: ${p:.2f}" for n, p in items]
    return "\n".join(lines + [f"TOTAL: ${total:.2f}"])


"""
================================================================================
4. WHAT IT SOLVES IN REALITY: UNABRIDGED PRODUCTION BREAKDOWN
================================================================================

PROBLEM 1: UNRELATED CHANGES COLLIDE
------------------------------------
- THE MESSY REALITY: Finance changes tax logic while Marketing redesigns the layout; both edit
  BadInvoice. Merge conflicts, and a layout tweak accidentally changes a total.
- THE SOLUTION: Different files, different owners.

PROBLEM 2: UNTESTABLE WITHOUT EVERYTHING
----------------------------------------
- THE MESSY REALITY: To test calculate_total() you also have to deal with db and SMTP
  because they live in the same class.
- THE SOLUTION: InvoiceCalculator().total(...) needs nothing else.

PROBLEM 3: REUSE
----------------
- THE MESSY REALITY: The Quote system needs the same pretty-printing but not the saving.
  You can't reuse half a god-class.
- THE SOLUTION: Reuse InvoiceFormatter on its own.

PROBLEM 4: SWAPPING ONE CONCERN
-------------------------------
- THE MESSY REALITY: Moving from SMTP to SendGrid means opening the pricing class.
- THE SOLUTION: Replace InvoiceMailer only.
"""

if __name__ == "__main__":
    inv = Invoice([("Keyboard", 49.99), ("Mouse", 19.50)])
    total = InvoiceCalculator().total(inv)
    InvoiceRepository().save("INV-1", inv)
    body = InvoiceFormatter().to_text(inv, total)
    InvoiceMailer().send("ada@example.com", body)

    print("\n--- Function-based ---")
    print(format_invoice(inv.items, calculate_total(inv.items)))
