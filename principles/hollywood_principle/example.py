"""
================================================================================
1. BAD CODE: THE CALLER MICROMANAGES EVERY STEP (THE RUSHED MVP)
================================================================================
Each task's user must remember the correct call order, and the cleanup step.
"""

class BadReportTask:
    def open_resources(self): print("[Bad] opening resources")
    def build_report(self): print("[Bad] building report")
    def close_resources(self): print("[Bad] closing resources")


def bad_main():
    task = BadReportTask()
    task.open_resources()        # ❌ Every caller must repeat this exact sequence
    task.build_report()
    task.close_resources()       # ❌ Forgotten on error paths => resource leak


"""
================================================================================
2. THE PRINCIPLE: "DON'T CALL US, WE'LL CALL YOU" (HOLLYWOOD PRINCIPLE)
================================================================================
Core Definition:
    High-level components control the flow and call low-level components
    at the right moments. Low-level components never call upward or manage
    the workflow. They just implement hooks.

The Golden Rule:
    If every user of your class must remember a call sequence, move the sequence
    into the framework (template method, callbacks, lifecycle hooks) and let the
    extension code simply "be called".
"""


"""
================================================================================
3. GOOD CODE: THE FRAMEWORK OWNS THE CONTROL FLOW
================================================================================
"""
from abc import ABC, abstractmethod
from typing import Callable, List

# ------------------------------------------------------------------------------
# APPROACH A: TEMPLATE METHOD (inheritance-based hooks)
# ------------------------------------------------------------------------------

class Task(ABC):
    def run(self) -> None:                 # The "framework" controls the algorithm
        self.setup()
        try:
            self.execute()
        finally:
            self.teardown()                # ALWAYS runs

    def setup(self) -> None: pass          # Optional hook
    def teardown(self) -> None: pass       # Optional hook

    @abstractmethod
    def execute(self) -> None: ...         # Required hook


class ReportTask(Task):
    def setup(self) -> None: print("[Report] opening resources")
    def execute(self) -> None: print("[Report] building report")
    def teardown(self) -> None: print("[Report] closing resources")


# ------------------------------------------------------------------------------
# APPROACH B: CALLBACK REGISTRATION (composition-based hooks)
# ------------------------------------------------------------------------------

class Scheduler:
    def __init__(self):
        self._jobs: List[Callable[[int], None]] = []

    def register(self, job: Callable[[int], None]) -> None:
        self._jobs.append(job)

    def tick(self, t: int) -> None:         # Scheduler calls jobs, not vice versa
        for job in self._jobs:
            job(t)


"""
================================================================================
4. WHAT IT SOLVES IN REALITY: UNABRIDGED PRODUCTION BREAKDOWN
================================================================================

PROBLEM 1: FORGOTTEN CLEANUP
----------------------------
- THE MESSY REALITY: One of fifty callers skips close_resources() on an error path. Connection
  pool exhausted at 3 AM.
- THE SOLUTION: The framework's run() wraps execute() in try/finally. Extension authors can't
  forget teardown.

PROBLEM 2: WRONG ORDER
----------------------
- THE MESSY REALITY: A new teammate calls build_report() before open_resources().
- THE SOLUTION: The order is code in exactly one place.

PROBLEM 3: CYCLIC DEPENDENCIES
------------------------------
- THE MESSY REALITY: Low-level modules call high-level ones, high-level calls low-level,
  producing circular imports and "who calls whom?" confusion.
- THE SOLUTION: Control flows downward only. The low-level code never imports the framework's
  orchestration.

PROBLEM 4: CROSS-CUTTING CHANGES
--------------------------------
- THE MESSY REALITY: Add timing/logging/metrics to every task by editing every caller.
- THE SOLUTION: Add it once inside run(); every task gets it.
"""

if __name__ == "__main__":
    print("--- Template Method ---")
    ReportTask().run()

    print("\n--- Callbacks ---")
    s = Scheduler()
    s.register(lambda t: print(f"[Job A] tick {t}"))
    s.register(lambda t: print(f"[Job B] tick {t}"))
    s.tick(1)
