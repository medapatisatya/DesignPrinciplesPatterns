"""
================================================================================
1. BAD CODE: THE LABEL PRINTER THAT DIGS THROUGH THE ORDER
================================================================================
CRITIQUE: The printer reaches Order -> Customer -> Address -> city. If Address
ever changes, a shipping-label class breaks.
"""

class BadAddress:
    def __init__(self, city: str, country: str):
        self.city, self.country = city, country

class BadCustomer:
    def __init__(self, name: str, address: BadAddress):
        self.name, self.address = name, address

class BadOrder:
    def __init__(self, order_id: str, customer: BadCustomer):
        self.order_id, self.customer = order_id, customer


class BadLabelPrinter:
    def print_label(self, order: BadOrder) -> str:
        # ❌ Four hops: order.customer.address.city / .country / customer.name
        return (f"#{order.order_id} -> {order.customer.name}, "
                f"{order.customer.address.city}, {order.customer.address.country}")


"""
================================================================================
2. THE PRINCIPLE: "ONLY TALK TO YOUR IMMEDIATE FRIENDS"
================================================================================
What Varies:
    The internal structure of Order/Customer/Address (e.g., multiple addresses,
    pickup points, structured vs. free-text addresses).

What Stays Stable:
    The need: "give me the shipping label text for this order."
"""


"""
================================================================================
3. GOOD CODE: EACH OBJECT EXPOSES WHAT OTHERS NEED AND HIDES THE REST
================================================================================
"""
# ------------------------------------------------------------------------------
# APPROACH A: CHAINED DELEGATION (each layer talks only to the next)
# ------------------------------------------------------------------------------

class Address:
    def __init__(self, city: str, country: str):
        self._city, self._country = city, country

    def one_line(self) -> str:
        return f"{self._city}, {self._country}"


class Customer:
    def __init__(self, name: str, address: Address):
        self._name = name
        self._address = address

    def shipping_name_and_place(self) -> str:
        return f"{self._name}, {self._address.one_line()}"   # talks to its own component


class Order:
    def __init__(self, order_id: str, customer: Customer):
        self._order_id = order_id
        self._customer = customer

    def shipping_label_text(self) -> str:
        return f"#{self._order_id} -> {self._customer.shipping_name_and_place()}"


class LabelPrinter:
    def print_label(self, order: Order) -> str:
        return order.shipping_label_text()      # talks to its parameter only


# ------------------------------------------------------------------------------
# APPROACH B: A FACADE / NARROW DTO (pass just the label data)
# ------------------------------------------------------------------------------

from dataclasses import dataclass

@dataclass(frozen=True)
class LabelData:
    order_id: str
    recipient: str
    place: str

def render_label(data: LabelData) -> str:
    return f"#{data.order_id} -> {data.recipient}, {data.place}"


"""
================================================================================
4. WHAT IT SOLVES IN REALITY: MONETARY AND PRODUCTION BREAKDOWN
================================================================================

PROBLEM 1: INTERNATIONAL EXPANSION
----------------------------------
- THE MESSY REALITY: Address gets split into street/district/postcode and 'city' becomes
  optional. Every chained access (order.customer.address.city) across invoicing, labels,
  tax, and analytics breaks.
- THE SOLUTION: Only Address.one_line() changes. No other class knew the field names.

PROBLEM 2: MULTIPLE SHIPPING ADDRESSES
--------------------------------------
- THE MESSY REALITY: Customers now have billing + shipping addresses. Which one does
  `customer.address` mean? Every caller guesses.
- THE SOLUTION: Customer decides internally which address is the shipping one.

PROBLEM 3: UNIT TESTING THE PRINTER
-----------------------------------
- THE MESSY REALITY: To test the printer you build three nested objects.
- THE SOLUTION: Provide any object with shipping_label_text(); done.

PROBLEM 4: DATA PRIVACY / GDPR
------------------------------
- THE MESSY REALITY: If everyone can reach into customer.address, you can't tell who uses
  which personal fields.
- THE SOLUTION: Personal data exits only through a few deliberately-named methods, which are
  easy to audit and mask.
"""

if __name__ == "__main__":
    print("--- Bad chain ---")
    bad = BadOrder("A-1", BadCustomer("Ada", BadAddress("Hyderabad", "IN")))
    print(BadLabelPrinter().print_label(bad))

    print("\n--- Delegation ---")
    order = Order("A-1", Customer("Ada", Address("Hyderabad", "IN")))
    print(LabelPrinter().print_label(order))

    print("\n--- Narrow data ---")
    print(render_label(LabelData("A-1", "Ada", "Hyderabad, IN")))
