"""
================================================================================
CHALLENGE: LOOSELY COUPLED DESIGNS (CLEAN SLATE)
================================================================================
PROBLEM CONTEXT:
When a user signs up, the system must send a welcome email, create a CRM record,
and post to a Slack channel. More reactions are coming (e.g., trial setup).

THE GOAL:
Build an EventBus so the publisher (SignupService) knows nothing about who is
listening.

YOUR MISSION:
1. Implement EventBus: subscribe / unsubscribe / publish.
2. Implement SignupService so it only publishes "user_signed_up".
3. Make all tests pass.
"""

import unittest
from typing import Callable, Dict, List
from collections import defaultdict


# ==============================================================================
# 🚨 STEP 1: THE BAD CODE (DO NOT USE THIS LOGIC)
# ==============================================================================
class BadSignupService:
    def __init__(self, mailer, crm, slack):
        self.mailer, self.crm, self.slack = mailer, crm, slack   # ❌ knows all three

    def sign_up(self, email: str) -> bool:
        self.mailer.send_welcome(email)
        self.crm.create_contact(email)
        self.slack.post(f"New user {email}")
        return True


# ==============================================================================
# 🛠️ STEP 2: YOUR SOLUTION AREA
# ==============================================================================
Handler = Callable[[dict], None]


class EventBus:
    """
    [TODO]:
      - subscribe(event: str, handler)
      - unsubscribe(event: str, handler)      (no error if handler isn't subscribed)
      - publish(event: str, payload: dict) -> int
            Calls every handler for that event in subscription order.
            A handler that raises must NOT stop the others.
            Returns the number of handlers that completed WITHOUT raising.
            Unknown event => returns 0.
    """
    def __init__(self):
        self.events_handlers = defaultdict(list)

    def subscribe(self, event: str, handler: Handler) -> None:
        self.events_handlers[event].append(handler)

    def unsubscribe(self, event: str, handler: Handler) -> None:
        if event in self.events_handlers:
            self.events_handlers[event].remove(handler)

    def publish(self, event: str, payload: dict) -> int:
        count = 0
        if event in self.events_handlers:
            for handler in self.events_handlers[event]:
                try:
                    handler(payload)
                    count += 1
                except Exception as e:
                    print(f"Got the following Exception {str(e)}")
        return count


class SignupService:
    """
    [TODO]:
      - __init__(self, bus: EventBus)
      - sign_up(email) -> bool
            Empty email => return False and publish nothing.
            Otherwise publish "user_signed_up" with payload {"email": email}; return True.
    """
    def __init__(self, bus: EventBus):
        self.bus = bus

    def sign_up(self, email: str) -> bool:
        if not email: return False
        self.bus.publish("user_signed_up", {"email": email})
        return True


# ==============================================================================
# 🧪 STEP 3: AUTOMATED TESTING FRAMEWORK (DO NOT CHANGE THE TEST METHODS)
# ==============================================================================
class TestLooseCouplingPatterns(unittest.TestCase):

    def test_multiple_subscribers_all_notified_in_order(self):
        bus, calls = EventBus(), []
        bus.subscribe("e", lambda p: calls.append(("a", p["x"])))
        bus.subscribe("e", lambda p: calls.append(("b", p["x"])))
        self.assertEqual(bus.publish("e", {"x": 1}), 2)
        self.assertEqual(calls, [("a", 1), ("b", 1)])

    def test_unknown_event_is_harmless(self):
        self.assertEqual(EventBus().publish("nobody-listens", {}), 0)

    def test_unsubscribe(self):
        bus, calls = EventBus(), []
        handler = lambda p: calls.append(1)
        bus.subscribe("e", handler)
        bus.unsubscribe("e", handler)
        self.assertEqual(bus.publish("e", {}), 0)
        self.assertEqual(calls, [])

    def test_unsubscribe_unknown_handler_is_safe(self):
        EventBus().unsubscribe("e", lambda p: None)

    def test_failing_handler_does_not_block_others(self):
        bus, calls = EventBus(), []
        def boom(p): raise RuntimeError("down")
        bus.subscribe("e", boom)
        bus.subscribe("e", lambda p: calls.append("ok"))
        self.assertEqual(bus.publish("e", {}), 1)
        self.assertEqual(calls, ["ok"])

    def test_signup_publishes_event(self):
        bus, seen = EventBus(), []
        bus.subscribe("user_signed_up", lambda p: seen.append(p))
        self.assertTrue(SignupService(bus).sign_up("a@b.com"))
        self.assertEqual(seen, [{"email": "a@b.com"}])

    def test_signup_rejects_empty_email_and_publishes_nothing(self):
        bus, seen = EventBus(), []
        bus.subscribe("user_signed_up", lambda p: seen.append(p))
        self.assertFalse(SignupService(bus).sign_up(""))
        self.assertEqual(seen, [])

    def test_new_reaction_needs_no_change_to_signup_service(self):
        bus, trial = EventBus(), []
        bus.subscribe("user_signed_up", lambda p: trial.append(p["email"]))
        SignupService(bus).sign_up("new@user.io")
        self.assertEqual(trial, ["new@user.io"])


if __name__ == "__main__":
    print("--- Initiating Automated Code Validation Tests ---")
    unittest.main()
