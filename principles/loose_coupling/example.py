"""
================================================================================
1. BAD CODE: THE STATION THAT KNOWS ITS DISPLAYS (THE RUSHED MVP)
================================================================================
The weather station holds direct references to each concrete display.
"""

class PhoneDisplay:
    def show(self, temp: float) -> None:
        print(f"[Phone] Temperature: {temp}°C")

class WebDisplay:
    def render(self, temp: float) -> None:
        print(f"[Web] Temperature: {temp}°C")


class BadWeatherStation:
    def __init__(self):
        self.phone = PhoneDisplay()   # ❌ Tight coupling: creates and knows concrete displays
        self.web = WebDisplay()

    def set_temperature(self, temp: float) -> None:
        # ❌ New display = edit this method. Each display has a different method name.
        self.phone.show(temp)
        self.web.render(temp)


"""
================================================================================
2. THE PRINCIPLE: "STRIVE FOR LOOSELY COUPLED DESIGNS BETWEEN OBJECTS THAT INTERACT"
================================================================================
Core Definition:
    Objects that interact should know as little as possible about each other.
    They should know only a minimal contract (e.g., "I can be notified").

The Golden Rule:
    If changing or adding object B forces edits in object A, they are tightly
    coupled. Introduce a thin interface (Observer / callback / event) so A only
    knows "someone is listening", not WHO.
"""


"""
================================================================================
3. GOOD CODE: THE OBSERVER PATTERN
================================================================================
"""
from abc import ABC, abstractmethod
from typing import Callable, List

# ------------------------------------------------------------------------------
# APPROACH A: CLASS-BASED OBSERVERS
# ------------------------------------------------------------------------------

class Observer(ABC):
    @abstractmethod
    def update(self, temp: float) -> None: ...


class WeatherStation:
    """Subject: knows only the Observer interface."""
    def __init__(self):
        self._observers: List[Observer] = []
        self._temp = 0.0

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def set_temperature(self, temp: float) -> None:
        self._temp = temp
        for obs in list(self._observers):
            obs.update(temp)


class GoodPhoneDisplay(Observer):
    def update(self, temp: float) -> None:
        print(f"[Phone] Temperature: {temp}°C")

class GoodWebDisplay(Observer):
    def update(self, temp: float) -> None:
        print(f"[Web] Temperature: {temp}°C")

class FrostAlert(Observer):  # Added later: station unchanged
    def update(self, temp: float) -> None:
        if temp <= 0:
            print("[Alert] Frost warning!")


# ------------------------------------------------------------------------------
# APPROACH B: CALLBACK-BASED (just functions)
# ------------------------------------------------------------------------------

class Thermometer:
    def __init__(self):
        self._listeners: List[Callable[[float], None]] = []

    def on_change(self, callback: Callable[[float], None]) -> None:
        self._listeners.append(callback)

    def set_temperature(self, temp: float) -> None:
        for cb in self._listeners:
            cb(temp)


"""
================================================================================
4. WHAT IT SOLVES IN REALITY: UNABRIDGED PRODUCTION BREAKDOWN
================================================================================

PROBLEM 1: EVERY NEW CONSUMER EDITS THE PRODUCER
------------------------------------------------
- THE MESSY REALITY: Adding a smartwatch display means editing BadWeatherStation, which three
  other teams also touch. Merge conflicts, regressions.
- THE SOLUTION: Write a new Observer, call attach(). The station never changes.

PROBLEM 2: RUNTIME SUBSCRIBE / UNSUBSCRIBE
------------------------------------------
- THE MESSY REALITY: A user closes the web tab. The bad station still calls its display.
- THE SOLUTION: detach(observer). The set of listeners is data, not code.

PROBLEM 3: ISOLATED TESTING
---------------------------
- THE MESSY REALITY: Testing station logic drags in real displays (and their I/O).
- THE SOLUTION: Attach a tiny recording observer or lambda.

PROBLEM 4: REUSING THE PRODUCER
-------------------------------
- THE MESSY REALITY: The station can't be reused in a project with different displays,
  because it creates PhoneDisplay and WebDisplay itself.
- THE SOLUTION: The station has zero knowledge of displays, so it drops into any project.
"""

if __name__ == "__main__":
    print("--- Class-Based Observers ---")
    station = WeatherStation()
    phone, web, frost = GoodPhoneDisplay(), GoodWebDisplay(), FrostAlert()
    for o in (phone, web, frost):
        station.attach(o)
    station.set_temperature(-2.0)
    print("\nWeb tab closed (detach)...")
    station.detach(web)
    station.set_temperature(21.5)

    print("\n--- Callback-Based ---")
    t = Thermometer()
    t.on_change(lambda temp: print(f"[Lambda] got {temp}"))
    t.set_temperature(10)
