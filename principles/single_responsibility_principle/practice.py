"""
================================================================================
CHALLENGE: SINGLE RESPONSIBILITY PRINCIPLE (CLEAN SLATE)
================================================================================
PROBLEM CONTEXT:
A shop's ReceiptManager computes totals with tax, formats the receipt text,
and stores receipts. Finance, Design and Platform all want to change it
independently.

THE GOAL:
Split it into focused classes, each with one reason to change, plus a thin
service that coordinates them.

YOUR MISSION:
1. ReceiptCalculator  : money math only.
2. ReceiptFormatter   : text layout only.
3. ReceiptStore       : persistence only.
4. ReceiptService     : coordinates the other three.
"""

import unittest
from typing import List, Tuple

Item = Tuple[str, float]

# ==============================================================================
# 🚨 STEP 1: THE BAD CODE (DO NOT USE THIS LOGIC)
# ==============================================================================
class BadReceiptManager:
    def __init__(self):
        self.saved = []

    def checkout(self, items: List[Item], tax_rate: float) -> str:
        total = round(sum(p for _, p in items) * (1 + tax_rate), 2)          # math
        text = "\n".join([f"{n}: ${p:.2f}" for n, p in items] +
                         [f"TOTAL: ${total:.2f}"])                           # layout
        self.saved.append(text)                                              # storage
        return text


# ==============================================================================
# 🛠️ STEP 2: YOUR SOLUTION AREA
# ==============================================================================
class ReceiptCalculator:
    """
    [TODO]: total(items, tax_rate) -> round(sum of prices * (1 + tax_rate), 2)
    """
    def total(self, items: List[Item], tax_rate: float) -> float:
        return round(sum(item[1] for item in items) * (1 + tax_rate), 2)


class ReceiptFormatter:
    """
    [TODO]: format(items, total) -> one line per item "name: $x.xx", then "TOTAL: $x.xx",
            all joined by "\\n".   Example: "Pen: $2.00\\nTOTAL: $2.20"
    """
    def format(self, items: List[Item], total: float) -> str:
        items_rec = []
        for item in items:
            items_rec.append(f"{item[0]}: ${item[1]:.2f}")
        items_rec.append(f"TOTAL: ${total:.2f}")
        return "\n".join(items_rec)


class ReceiptStore:
    """
    [TODO]:
      - save(text)     : remember a receipt
      - all() -> list  : return the saved receipts, in order (return a COPY)
    """
    def __init__(self):
        self.receipts = []

    def save(self, text: str) -> None:
        self.receipts.append(text)

    def all(self) -> List[str]:
        return self.receipts.copy()


class ReceiptService:
    """
    [TODO]:
      - __init__(self, calculator, formatter, store)
      - checkout(items, tax_rate) -> str
            Empty items => raise ValueError and save nothing.
            Otherwise: total -> format -> save -> return the text.
    """
    def __init__(self, calculator, formatter, store):
        self.calculator, self.formatter, self.store = calculator, formatter, store

    def checkout(self, items: List[Item], tax_rate: float) -> str:
        if items: 
            total = self.calculator.total(items, tax_rate)
            receipt = self.formatter.format(items, total)
            self.store.save(receipt)
            return receipt
        else:
            raise ValueError("Cart is empty")



# ==============================================================================
# 🧪 STEP 3: AUTOMATED TESTING FRAMEWORK (DO NOT CHANGE THE TEST METHODS)
# ==============================================================================
class TestSingleResponsibilityPatterns(unittest.TestCase):

    def test_calculator_alone(self):
        self.assertEqual(ReceiptCalculator().total([("Pen", 2.0)], 0.10), 2.20)
        self.assertEqual(ReceiptCalculator().total([("A", 1.0), ("B", 2.0)], 0.0), 3.0)

    def test_formatter_alone(self):
        text = ReceiptFormatter().format([("Pen", 2.0)], 2.2)
        self.assertEqual(text, "Pen: $2.00\nTOTAL: $2.20")

    def test_store_alone_returns_copy(self):
        store = ReceiptStore()
        store.save("r1"); store.save("r2")
        self.assertEqual(store.all(), ["r1", "r2"])
        store.all().append("hack")
        self.assertEqual(store.all(), ["r1", "r2"])

    def test_service_coordinates_real_collaborators(self):
        store = ReceiptStore()
        svc = ReceiptService(ReceiptCalculator(), ReceiptFormatter(), store)
        text = svc.checkout([("Pen", 2.0)], 0.10)
        self.assertEqual(text, "Pen: $2.00\nTOTAL: $2.20")
        self.assertEqual(store.all(), [text])

    def test_service_uses_only_collaborators(self):
        class FakeCalc:
            def total(self, items, tax_rate): return 99.0
        class FakeFormatter:
            def format(self, items, total): return f"FAKE {total}"
        class FakeStore:
            def __init__(self): self.saved = []
            def save(self, text): self.saved.append(text)
        store = FakeStore()
        out = ReceiptService(FakeCalc(), FakeFormatter(), store).checkout([("X", 1.0)], 0.5)
        self.assertEqual(out, "FAKE 99.0")
        self.assertEqual(store.saved, ["FAKE 99.0"])

    def test_empty_cart_rejected_and_not_saved(self):
        store = ReceiptStore()
        svc = ReceiptService(ReceiptCalculator(), ReceiptFormatter(), store)
        with self.assertRaises(ValueError):
            svc.checkout([], 0.1)
        self.assertEqual(store.all(), [])


if __name__ == "__main__":
    print("--- Initiating Automated Code Validation Tests ---")
    unittest.main()
