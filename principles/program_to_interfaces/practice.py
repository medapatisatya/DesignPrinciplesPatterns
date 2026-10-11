"""
================================================================================
CHALLENGE: PROGRAM TO INTERFACES, NOT IMPLEMENTATIONS (CLEAN SLATE)
================================================================================
PROBLEM CONTEXT:
A reporting module must export a list of records (dicts) as JSON or CSV today,
and as plain text, XML, etc. in the coming weeks.

THE GOAL:
ReportGenerator must depend ONLY on an abstract Exporter interface, never on
JsonExporter or CsvExporter directly.

YOUR MISSION:
1. Make Exporter a true interface (it already is abstract; implement the children).
2. Implement JsonExporter and CsvExporter.
3. Implement ReportGenerator so it works with ANY Exporter.
"""

import json
import unittest
from abc import ABC, abstractmethod
from typing import List

# ==============================================================================
# 🚨 STEP 1: THE BAD CODE (DO NOT USE THIS LOGIC)
# ==============================================================================
class BadReportGenerator:
    def generate(self, records: list, fmt: str) -> str:
        if not records:
            return ""
        if fmt == "json":
            return json.dumps(records)
        elif fmt == "csv":
            header = ",".join(records[0].keys())
            rows = [",".join(str(v) for v in r.values()) for r in records]
            return "\n".join([header] + rows)
        raise ValueError(fmt)


# ==============================================================================
# 🛠️ STEP 2: YOUR SOLUTION AREA
# ==============================================================================
class Exporter(ABC):
    @abstractmethod
    def export(self, records: List[dict]) -> str:
        """Turn records into a string representation."""


class JsonExporter(Exporter):
    def export(self, records: List[dict]) -> str:
        return json.dumps(records)


class CsvExporter(Exporter):
    def export(self, records: List[dict]) -> str:
        csv_records = [",".join(records[0].keys())]
        for record in records:
            csv_records.append(",".join([str(x) for x in record.values()]))
        return "\n".join(csv_records)


class ReportGenerator:
    def __init__(self, exporter: Exporter):
        self.exporter = exporter

    def generate(self, records: List[dict]) -> str:
        if not records: return ""
        return self.exporter.export(records)


# ==============================================================================
# 🧪 STEP 3: AUTOMATED TESTING FRAMEWORK (DO NOT CHANGE THE TEST METHODS)
# ==============================================================================
class TestInterfacePatterns(unittest.TestCase):

    def setUp(self):
        self.records = [{"name": "Ada", "age": 36}, {"name": "Linus", "age": 28}]

    def test_interface_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            Exporter()

    def test_implementations_honour_the_interface(self):
        self.assertIsInstance(JsonExporter(), Exporter)
        self.assertIsInstance(CsvExporter(), Exporter)

    def test_json_exporter(self):
        out = JsonExporter().export(self.records)
        self.assertEqual(json.loads(out), self.records)

    def test_csv_exporter(self):
        self.assertEqual(CsvExporter().export(self.records), "name,age\nAda,36\nLinus,28")

    def test_generator_delegates_to_any_exporter(self):
        self.assertEqual(ReportGenerator(CsvExporter()).generate(self.records),
                         "name,age\nAda,36\nLinus,28")
        self.assertEqual(json.loads(ReportGenerator(JsonExporter()).generate(self.records)),
                         self.records)

    def test_generator_accepts_brand_new_exporter(self):
        class CountExporter(Exporter):
            def export(self, records):
                return f"{len(records)} records"
        self.assertEqual(ReportGenerator(CountExporter()).generate(self.records), "2 records")

    def test_empty_records_rule_is_in_the_generator(self):
        class ExplodingExporter(Exporter):
            def export(self, records):
                raise AssertionError("should not be called for empty input")
        self.assertEqual(ReportGenerator(ExplodingExporter()).generate([]), "")


if __name__ == "__main__":
    print("--- Initiating Automated Code Validation Tests ---")
    unittest.main()
