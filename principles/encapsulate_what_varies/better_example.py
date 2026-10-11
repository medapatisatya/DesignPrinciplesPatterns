"""
================================================================================
1. BAD CODE: THE HARDCODED PAYMENT MONOLITH (THE MAINTENANCE TRAP)
================================================================================
In this script, the BillingEngine is tightly coupled to every payment vendor's
specific SDK logic, error signatures, and workflows.

CRITIQUE: Adding Apple Pay or fixing a PayPal bug requires changing this file,
which risks knocking out the entire company's revenue engine.
"""

class BadBillingEngine:
    def process_payment(self, amount: float, gateway: str, payment_details: dict) -> bool:
        print(f"[Engine] Starting transaction of ${amount}...")
        
        # ❌ CRITICAL ANTI-PATTERN: The core engine has explicit knowledge of vendor specs.
        if gateway == "stripe":
            try:
                # Imagine concrete Stripe SDK calls here
                print(f"Connecting to Stripe API using token: {payment_details.get('stripe_token')}")
                if amount <= 0: raise ValueError("Stripe: Invalid Amount")
                print("Stripe transaction settled successfully.")
                return True
            except Exception as e:
                print(f"Logging Stripe failure: {e}")
                return False
                
        elif gateway == "paypal":
            # PayPal handles transactions differently (e.g., using email and express checkout URLs)
            print(f"Connecting to PayPal for user: {payment_details.get('paypal_email')}")
            print("Redirecting user to PayPal approval portal...")
            # Imagine complex PayPal SDK handling here
            return True
            
        elif gateway == "apple_pay":
            # Apple Pay uses tokenized biometrics from iOS devices
            print(f"Decrypting Apple Pay cryptogram: {payment_details.get('apple_token')}")
            return True
            
        else:
            raise ValueError(f"Unsupported gateway: {gateway}")


"""
================================================================================
2. THE PRINCIPLE: "ENCAPSULATE WHAT VARIES"
================================================================================
What Varies: 
    The underlying third-party APIs, SDK packages, custom error structures, and
    authentication mechanics required by different payment companies.

What Stays Stable: 
    The high-level core business rule: Taking a specific financial amount from 
    a customer and returning a simple True (Success) or False (Failure).
"""


"""
================================================================================
3. GOOD CODE: THE ENCAPSULATED PLUG-AND-PLAY ARCHITECTURE
================================================================================
"""
from abc import ABC, abstractmethod

# ------------------------------------------------------------------------------
# APPROACH A: CLASS-BASED ENCAPSULATION (Best for complex SDKs with heavy state)
# ------------------------------------------------------------------------------

class PaymentGateway(ABC):
    """The Immutable Boundary. The engine only interacts with this contract."""
    @abstractmethod
    def charge(self, amount: float, details: dict) -> bool:
        pass


class StripeGateway(PaymentGateway):
    def charge(self, amount: float, details: dict) -> bool:
        try:
            print(f"[Stripe SDK] Charging card token {details.get('stripe_token')} for ${amount}")
            return True
        except Exception as stripe_error:
            # Handle, normalize, and log Stripe-specific errors here
            print(f"[Stripe Error] {stripe_error}")
            return False


class PayPalGateway(PaymentGateway):
    def charge(self, amount: float, details: dict) -> bool:
        print(f"[PayPal SDK] Initiating express token for {details.get('paypal_email')}")
        print(f"[PayPal SDK] Capturing transaction of ${amount}")
        return True


class CleanBillingEngine:
    """The Core Core Engine: Completely insulated from vendor changes."""
    def __init__(self, gateway: PaymentGateway):
        self.gateway = gateway  # The gateway variation is injected cleanly

    def process_payment(self, amount: float, payment_details: dict) -> bool:
        print(f"[CleanEngine] Executing financial transaction rules...")
        # The engine doesn't care HOW the charge happens, only that the contract is fulfilled
        success = self.gateway.charge(amount, payment_details)
        
        if success:
            print("[CleanEngine] Internal ledger updated. Order marked as PAID.")
        else:
            print("[CleanEngine] Internal ledger updated. Order marked as FAILED.")
        return success


# ------------------------------------------------------------------------------
# APPROACH B: FUNCTION-BASED ENCAPSULATION (Best for stateless, quick API calls)
# ------------------------------------------------------------------------------

def process_stripe(amount: float, details: dict) -> bool:
    print(f"[Functional Stripe] Charging ${amount}")
    return True

def process_paypal(amount: float, details: dict) -> bool:
    print(f"[Functional PayPal] Charging ${amount}")
    return True

# Map vendors directly into a clean registry dictionary
GATEWAY_REGISTRY = {
    "stripe": process_stripe,
    "paypal": process_paypal
}

class FunctionalBillingEngine:
    def process_payment(self, amount: float, gateway_name: str, payment_details: dict) -> bool:
        # Dynamically fish out the correct execution function
        payment_handler = GATEWAY_REGISTRY.get(gateway_name)
        if not payment_handler:
            print(f"Error: Unknown gateway '{gateway_name}'")
            return False
            
        return payment_handler(amount, payment_details)


"""
================================================================================
4. WHAT IT SOLVES IN REALITY: MONETARY AND PRODUCTION BREAKDOWN
================================================================================

PROBLEM 1: THIRD-PARTY SDK BREAKING CHANGES (UPGRADE HELL)
-----------------------------------------------------------
- THE MESSY REALITY: Stripe updates its official library from version 2 to version 3. 
  The new SDK alters the layout of response variables. In the 'Bad Code', updating 
  the Stripe code forces you to open the shared file containing the system's entire billing 
  architecture. A simple copy-paste error or missing bracket while editing the Stripe block 
  accidentally breaks the logic handling PayPal orders. Your entire application crashes, 
  and the company drops to $0 revenue for hours.
- THE SOLUTION: The code is compartmentalized. You completely rewrite the internal implementation 
  of 'StripeGateway' inside an isolated file. The 'PayPalGateway' is untouched, uncompiled, and 
  architecturally safe. The blast radius of an SDK change is physically bound to one class.

PROBLEM 2: COMPLEX WEBHOOK AND FAILURE TESTING
-----------------------------------------------
- THE MESSY REALITY: The business asks you to handle card declines smoothly. Testing code 
  failures in the 'Bad Code' forces you to trigger the main checkout orchestrator, mock deep 
  application database logic, and simulate a full checkout event just to check if the logic 
  catches a bad card number. It is difficult, slow, and engineers bypass testing it.
- THE SOLUTION: You test the strategy directly. Pass an expired card dictionary to 
  'StripeGateway.charge()' in an isolated script. You can mock the HTTP call and verify your error 
  handling logic in milliseconds, completely bypassing the main application engine.

PROBLEM 3: COMPLIANCE AND AUDITING (PCI SECURITY AUDITS)
---------------------------------------------------------
- THE MESSY REALITY: To achieve PCI compliance, security officers must carefully audit how your 
  system handles raw payment tokens and sensitive information. In the 'Bad Code', they have to 
  manually look through your entire workflow file because token decryption logic is mixed directly 
  in with order histories, shipping calls, and standard data operations.
- THE SOLUTION: You point the security auditors to the isolated payment strategy files. The core 
  system 'CleanBillingEngine' handles no raw tokens, no financial encryption keys, and zero API credentials. 
  It vastly simplifies security audits because the perimeter is cleanly defined.

PROBLEM 4: DYNAMIC MULTI-GATEWAY FAILOVER
------------------------------------------
- THE MESSY REALITY: Stripe goes down globally due to an infrastructure outage. You need to route 
  all payments to PayPal immediately to avoid losing millions. In the 'Bad Code', you must rapidly 
  write hotfixes, alter complex 'if/else' paths under pressure, and rush an emergency production 
  code deployment, praying you don't introduce a typo.
- THE SOLUTION: Because you decoupled the engines using a consistent interface registry, your 
  billing framework can read the active gateway choice directly from an environment flag or database 
  toggle. If Stripe goes offline, an operational script swaps the engine's current gateway instance to 
  'PayPalGateway' instantly at runtime without rewriting code or deploying changes.
"""

# Concrete execution test
if __name__ == "__main__":
    print("--- Executing Isolated Class-Based Payment Systems ---")
    # We dynamically pass the desired strategy right into the stable engine
    stripe_engine = CleanBillingEngine(gateway=StripeGateway())
    stripe_engine.process_payment(49.99, {"stripe_token": "tok_12345XYZ"})
    
    print("\nSwitching gateways cleanly...")
    paypal_engine = CleanBillingEngine(gateway=PayPalGateway())
    paypal_engine.process_payment(89.99, {"paypal_email": "customer@email.com"})

    print("\n--- Executing Functional Lookup Payment Systems ---")
    func_engine = FunctionalBillingEngine()
