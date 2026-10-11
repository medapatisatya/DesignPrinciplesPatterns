"""
================================================================================
CHALLENGE: DEPENDENCY INVERSION PRINCIPLE (CLEAN SLATE)
================================================================================
PROBLEM CONTEXT:
A reminder system sends messages to users once they are due. It needs the
current time and a way to deliver messages (email today, push tomorrow).

THE GOAL:
ReminderService (high-level policy) must depend ONLY on the abstractions
Notifier and Clock. Real implementations are plugged in from outside, and tests
use fakes (no sleeping, no real emails).

YOUR MISSION:
1. Implement SystemClock (a real Clock).
2. Implement ReminderService using the injected abstractions.
3. Make all tests pass.
"""

import unittest
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List

# ==============================================================================
# 🚨 STEP 1: THE BAD CODE (DO NOT USE THIS LOGIC)
# ==============================================================================
class BadReminderService:
    def __init__(self):
        self.reminders = []

    def send_due(self) -> int:
        now = datetime.now()                          # ❌ hidden dependency on real time
        sent = 0
        for user, text, due in self.reminders:
            if due <= now:
                print(f"[SMTP] to {user}: {text}")    # ❌ hardwired delivery
                sent += 1
        return sent


# ==============================================================================
# 🛠️ STEP 2: YOUR SOLUTION AREA
# ==============================================================================
class Notifier(ABC):
    @abstractmethod
    def send(self, user: str, text: str) -> None: ...

class Clock(ABC):
    @abstractmethod
    def now(self) -> datetime: ...


class SystemClock(Clock):
    def now(self):
        return datetime.now()


class ReminderService:
    """
    [TODO]:
      - __init__(self, notifier: Notifier, clock: Clock)
      - add_reminder(user: str, text: str, due: datetime)
      - send_due_reminders() -> int
            Sends (via notifier.send(user, text)) every reminder whose due time is
            <= clock.now() and which has NOT been sent before.
            Returns how many were sent in THIS call.
    """
    def __init__(self, notifier: Notifier, clock: Clock):
        self.notifier = notifier
        self.clock = clock
        self.reminders = []

    def add_reminder(self, user: str, text: str, due: datetime) -> None:
        self.reminders.append([user, text, due])

    def send_due_reminders(self) -> int:
        sent = 0
        due_reminders = []
        for i in range(len(self.reminders)):
            user, text, due = self.reminders[i]
            if due <= self.clock.now():
                self.notifier.send(user, text)
                sent += 1
            else:
                due_reminders.append(self.reminders[i])
        self.reminders = due_reminders
        return sent
            


# ==============================================================================
# 🧪 STEP 3: AUTOMATED TESTING FRAMEWORK (DO NOT CHANGE THE TEST METHODS)
# ==============================================================================
class FakeClock(Clock):
    def __init__(self, start: datetime): self.current = start
    def now(self) -> datetime: return self.current
    def advance(self, **kwargs) -> None: self.current += timedelta(**kwargs)

class RecordingNotifier(Notifier):
    def __init__(self): self.sent: List[tuple] = []
    def send(self, user: str, text: str) -> None: self.sent.append((user, text))


class TestDependencyInversionPatterns(unittest.TestCase):

    def setUp(self):
        self.t0 = datetime(2026, 1, 1, 9, 0, 0)
        self.clock = FakeClock(self.t0)
        self.notifier = RecordingNotifier()
        self.service = ReminderService(self.notifier, self.clock)

    def test_system_clock_is_a_clock(self):
        clock = SystemClock()
        self.assertIsInstance(clock, Clock)
        self.assertIsInstance(clock.now(), datetime)

    def test_nothing_sent_before_due_time(self):
        self.service.add_reminder("ada", "stand-up", self.t0 + timedelta(hours=1))
        self.assertEqual(self.service.send_due_reminders(), 0)
        self.assertEqual(self.notifier.sent, [])

    def test_sent_once_due(self):
        self.service.add_reminder("ada", "stand-up", self.t0 + timedelta(hours=1))
        self.clock.advance(hours=1)
        self.assertEqual(self.service.send_due_reminders(), 1)
        self.assertEqual(self.notifier.sent, [("ada", "stand-up")])

    def test_reminder_is_never_sent_twice(self):
        self.service.add_reminder("ada", "stand-up", self.t0)
        self.assertEqual(self.service.send_due_reminders(), 1)
        self.assertEqual(self.service.send_due_reminders(), 0)
        self.assertEqual(len(self.notifier.sent), 1)

    def test_only_due_reminders_are_sent(self):
        self.service.add_reminder("ada", "early", self.t0)
        self.service.add_reminder("bob", "late", self.t0 + timedelta(days=1))
        self.assertEqual(self.service.send_due_reminders(), 1)
        self.assertEqual(self.notifier.sent, [("ada", "early")])
        self.clock.advance(days=1)
        self.assertEqual(self.service.send_due_reminders(), 1)
        self.assertEqual(self.notifier.sent[-1], ("bob", "late"))

    def test_any_notifier_implementation_works(self):
        class UpperNotifier(Notifier):
            def __init__(self): self.out = []
            def send(self, user, text): self.out.append(f"{user.upper()}:{text.upper()}")
        n = UpperNotifier()
        svc = ReminderService(n, self.clock)
        svc.add_reminder("ada", "hi", self.t0)
        svc.send_due_reminders()
        self.assertEqual(n.out, ["ADA:HI"])


if __name__ == "__main__":
    print("--- Initiating Automated Code Validation Tests ---")
    unittest.main()
