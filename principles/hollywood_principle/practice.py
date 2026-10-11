"""
================================================================================
CHALLENGE: HOLLYWOOD PRINCIPLE (CLEAN SLATE)
================================================================================
PROBLEM CONTEXT:
Your data team runs nightly batch jobs: extract -> transform -> load. Some
jobs need setup (open a connection) and teardown (close it). Engineers keep
forgetting teardown when something fails.

THE GOAL:
Build a BatchJob framework. Job authors implement hooks; the framework
decides WHEN to call them ("Don't call us, we'll call you").

YOUR MISSION:
Implement BatchJob.run() with this exact flow:
    setup() -> extract() -> transform(data) -> load(data) -> teardown()
Rules:
  * teardown() ALWAYS runs, even if a step raised.
  * If any step raises, remaining steps are skipped, run() returns False.
  * If everything succeeds, run() returns True.
  * setup()/teardown() are optional hooks (default: do nothing).
"""

import unittest
from abc import ABC, abstractmethod

# ==============================================================================
# 🚨 STEP 1: THE BAD CODE (DO NOT USE THIS LOGIC)
# ==============================================================================
def bad_run_job(job):
    job.setup()
    data = job.extract()
    data = job.transform(data)
    job.load(data)
    job.teardown()        # ❌ skipped if extract/transform/load raise; each caller repeats this


# ==============================================================================
# 🛠️ STEP 2: YOUR SOLUTION AREA
# ==============================================================================
class BatchJob(ABC):
    @abstractmethod
    def extract(self):
        """Required hook: return raw data."""

    @abstractmethod
    def transform(self, data):
        """Required hook: return transformed data."""

    @abstractmethod
    def load(self, data) -> None:
        """Required hook: persist data."""

    def setup(self) -> None:
        """Optional hook."""

    def teardown(self) -> None:
        """Optional hook."""

    def run(self) -> bool:
        ret = True
        try:
            self.setup()
            data = self.extract()
            data = self.transform(data)
            self.load(data)
        except Exception as e:
            ret = False
        finally:
            self.teardown()
        return ret

# ==============================================================================
# 🧪 STEP 3: AUTOMATED TESTING FRAMEWORK (DO NOT CHANGE THE TEST METHODS)
# ==============================================================================
class RecordingJob(BatchJob):
    def __init__(self, fail_at: str = ""):
        self.calls = []
        self.fail_at = fail_at
        self.loaded = None

    def _maybe_fail(self, step: str):
        if self.fail_at == step:
            raise RuntimeError(f"{step} failed")

    def setup(self):
        self.calls.append("setup"); self._maybe_fail("setup")

    def extract(self):
        self.calls.append("extract"); self._maybe_fail("extract")
        return [1, 2, 3]

    def transform(self, data):
        self.calls.append("transform"); self._maybe_fail("transform")
        return [x * 10 for x in data]

    def load(self, data):
        self.calls.append("load"); self._maybe_fail("load")
        self.loaded = data

    def teardown(self):
        self.calls.append("teardown")


class TestHollywoodPatterns(unittest.TestCase):

    def test_happy_path_order_and_result(self):
        job = RecordingJob()
        self.assertTrue(job.run())
        self.assertEqual(job.calls, ["setup", "extract", "transform", "load", "teardown"])
        self.assertEqual(job.loaded, [10, 20, 30])

    def test_extract_failure_skips_rest_but_tears_down(self):
        job = RecordingJob(fail_at="extract")
        self.assertFalse(job.run())
        self.assertEqual(job.calls, ["setup", "extract", "teardown"])

    def test_transform_failure(self):
        job = RecordingJob(fail_at="transform")
        self.assertFalse(job.run())
        self.assertEqual(job.calls, ["setup", "extract", "transform", "teardown"])
        self.assertIsNone(job.loaded)

    def test_load_failure(self):
        job = RecordingJob(fail_at="load")
        self.assertFalse(job.run())
        self.assertEqual(job.calls[-1], "teardown")

    def test_setup_failure_still_tears_down_and_skips_work(self):
        job = RecordingJob(fail_at="setup")
        self.assertFalse(job.run())
        self.assertEqual(job.calls, ["setup", "teardown"])

    def test_optional_hooks_can_be_omitted(self):
        class MinimalJob(BatchJob):
            def __init__(self): self.out = None
            def extract(self): return "abc"
            def transform(self, data): return data.upper()
            def load(self, data): self.out = data
        job = MinimalJob()
        self.assertTrue(job.run())
        self.assertEqual(job.out, "ABC")

    def test_framework_cannot_be_instantiated_without_required_hooks(self):
        with self.assertRaises(TypeError):
            BatchJob()


if __name__ == "__main__":
    print("--- Initiating Automated Code Validation Tests ---")
    unittest.main()
