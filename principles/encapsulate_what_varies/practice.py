"""
================================================================================
CHALLENGE: ENCAPSULATE WHAT VARIES (CLEAN SLATE)
================================================================================
PROBLEM CONTEXT:
You manage an enterprise notification system. Currently, the system supports 
Email, SMS, and Slack notifications. The business team wants to add WhatsApp 
next week, and Teams the week after. 

THE GOAL:
Refactor the system entirely. Pull out the volatile channel logic and 
encapsulate it so that the main orchestration engine remains completely 
untouched when channels are added or modified.

YOUR MISSION:
1. Define how your varying behaviors are structured (Classes, Functions, etc.).
2. Implement your notification engines for email, sms, and slack.
3. Wire them into the RefactoredNotificationEngine so that the tests pass.
"""
from abc import ABC, abstractmethod
import unittest

# ==============================================================================
# 🚨 STEP 1: THE BAD CODE (DO NOT USE THIS LOGIC)
# ==============================================================================
class BadNotificationEngine:
    """
    CRITIQUE: This engine is rigid. Every new channel forces us to open this 
    monolithic block, increasing the risk of code regression and merge conflicts.
    """
    def send(self, channel: str, user_data: dict, message: str) -> bool:
        if not message:
            return False
            
        if channel == "email":
            print(f"[Email API] Sending to {user_data.get('email')}: {message}")
            return True
        elif channel == "sms":
            print(f"[SMS Provider] Sending to {user_data.get('phone')}: {message}")
            return True
        elif channel == "slack":
            print(f"[Slack Hook] Posting to channel {user_data.get('slack_id')}: {message}")
            return True
        else:
            return False


# ==============================================================================
# 🛠️ STEP 2: YOUR SOLUTION AREA (WRITE YOUR INFRASTRUCTURE HERE)
# ==============================================================================

# [TODO]: Define your abstract interfaces, strategies, registry maps, or functions here.
# Make sure you handle implementations for:
# - email (needs to verify user_data has 'email')
# - sms (needs to verify user_data has 'phone')
# - slack (needs to verify user_data has 'slack_id')


class RefactoredNotificationEngine:
    """
    The core stable engine. It must remain 100% agnostic of how individual 
    third-party notification APIs actually connect or process data.
    """
    @abstractmethod
    def send_notification(self, user_data: dict, message: str) -> bool:
        pass


class EmailNotificationEngine(RefactoredNotificationEngine):
    def send_notification(self, user_data: dict, message: str) -> bool:
        if not "email" in user_data or not message: return False
        print(f"Sending email to {user_data["email"]} with content {message}")
        return True

class SMSNotificationEngine(RefactoredNotificationEngine):
    def send_notification(self, user_data: dict, message: str):
        if not "phone" in user_data or not message: return False
        print(f"Sending sms to {user_data["phone"]} with content {message}")
        return True

class SlackNotificationEngine(RefactoredNotificationEngine):
    def send_notification(self, user_data: dict, message: str):
        if not "slack_id" in user_data or not message: return False
        print(f"Sending message to {user_data["slack_id"]} with content {message}")
        return True

# ==============================================================================
# 🧪 STEP 3: AUTOMATED TESTING FRAMEWORK (DO NOT CHANGE THE TEST METHODS)
# ==============================================================================
class TestNotificationPatterns(unittest.TestCase):
    
    def setUp(self):
        self.mock_user = {
            "email": "dev@test.com",
            "phone": "+15550199",
            "slack_id": "C_DEV_TEAM"
        }

    def test_empty_message_rejection(self):
        """Stable business rules should catch empty strings instantly."""
        # Adjust instantiation below to match your pattern if needed, but ensure it rejects empty text
        engine = EmailNotificationEngine() 
        # Note: You can pass your strategy here depending on how you implement __init__
        try:
            # If your init requires a strategy parameter, adapt this line to make the test run
            self.assertFalse(engine.send_notification(self.mock_user, ""))
        except TypeError:
            # This is a fallback in case you chose an alternative approach
            pass

    # Note: To wire these tests up to your custom architecture, you may adjust 
    # the way 'engine' is created in the lines below so it uses your new classes/registry.
    
    def test_isolated_email_dispatch(self):
        """Validates that the email component performs its work accurately."""
        engine = EmailNotificationEngine() 
        self.assertTrue(engine.send_notification(self.mock_user, "Hello Email World"))

    def test_isolated_sms_dispatch(self):
        """Validates that the SMS component performs its work accurately."""
        engine = SMSNotificationEngine()
        self.assertTrue(engine.send_notification(self.mock_user, "Hello SMS World"))

    def test_isolated_slack_dispatch(self):
        """Validates that the Slack component performs its work accurately."""
        engine = SlackNotificationEngine()
        self.assertTrue(engine.send_notification(self.mock_user, "Hello Slack World"))


if __name__ == "__main__":
    print("--- Initiating Automated Code Validation Tests ---")
    unittest.main()
