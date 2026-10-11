"""
================================================================================
1. BAD CODE: PLUGINS THAT DRIVE THE APPLICATION
================================================================================
CRITIQUE: Each plugin reaches up and calls the host to register itself,
initialize services, and set up routes, in whatever order the author guessed.
"""

class BadHost:
    def __init__(self):
        self.routes = {}
        self.db_ready = False
    def init_db(self): self.db_ready = True
    def add_route(self, path: str, fn): self.routes[path] = fn


class BadPlugin:
    def start(self, host: BadHost) -> None:
        host.init_db()                                  # ❌ plugin controls the host's lifecycle
        host.add_route("/hello", lambda: "hello")       # ❌ if two plugins call init_db(): chaos


"""
================================================================================
2. THE PRINCIPLE: "DON'T CALL US, WE'LL CALL YOU"
================================================================================
What Varies:
    What each plugin does when loaded, when events arrive, and when unloaded.

What Stays Stable:
    The lifecycle: load -> (handle events)* -> unload, with failure isolation.
"""


"""
================================================================================
3. GOOD CODE: THE HOST CALLS THE PLUGINS' HOOKS
================================================================================
"""
from abc import ABC
from typing import Dict, List

# ------------------------------------------------------------------------------
# APPROACH A: LIFECYCLE HOOKS (plugins implement; the host calls)
# ------------------------------------------------------------------------------

class Plugin(ABC):
    """All hooks are optional. Plugins never call the host."""
    name = "unnamed"
    def on_load(self) -> None: pass
    def on_event(self, event: str, payload: dict) -> None: pass
    def on_unload(self) -> None: pass


class PluginHost:
    def __init__(self):
        self._plugins: List[Plugin] = []
        self.errors: List[str] = []

    def register(self, plugin: Plugin) -> None:
        self._plugins.append(plugin)

    def start(self) -> None:
        for p in self._plugins:
            self._safe(p, p.on_load)

    def dispatch(self, event: str, payload: dict) -> None:
        for p in self._plugins:
            self._safe(p, lambda p=p: p.on_event(event, payload))

    def stop(self) -> None:
        for p in reversed(self._plugins):     # reverse order, like stacking/unstacking
            self._safe(p, p.on_unload)

    def _safe(self, plugin: Plugin, call) -> None:
        try:
            call()
        except Exception as exc:
            self.errors.append(f"{plugin.name}: {exc}")


# --- Plugins: just hooks, no orchestration -----------------------------------
class AuditPlugin(Plugin):
    name = "audit"
    def on_load(self): print("[audit] ready")
    def on_event(self, event, payload): print(f"[audit] saw {event} {payload}")
    def on_unload(self): print("[audit] flushed")

class BrokenPlugin(Plugin):
    name = "broken"
    def on_event(self, event, payload): raise RuntimeError("boom")

class MetricsPlugin(Plugin):
    name = "metrics"
    def __init__(self): self.count = 0
    def on_event(self, event, payload): self.count += 1
    def on_unload(self): print(f"[metrics] total events: {self.count}")


# ------------------------------------------------------------------------------
# APPROACH B: DECORATOR-STYLE EVENT HOOKS (framework-style registration)
# ------------------------------------------------------------------------------

class MiniApp:
    def __init__(self):
        self._handlers: Dict[str, list] = {}

    def on(self, event: str):
        def decorator(fn):
            self._handlers.setdefault(event, []).append(fn)
            return fn
        return decorator

    def emit(self, event: str, payload: dict) -> list:
        return [fn(payload) for fn in self._handlers.get(event, [])]


"""
================================================================================
4. WHAT IT SOLVES IN REALITY: MONETARY AND PRODUCTION BREAKDOWN
================================================================================

PROBLEM 1: ONE BAD PLUGIN TAKES DOWN THE PLATFORM
-------------------------------------------------
- THE MESSY REALITY: A third-party plugin throws during startup. With plugins driving the host,
  the whole app fails to boot.
- THE SOLUTION: The host calls each hook inside its own safety net and records errors.

PROBLEM 2: LIFECYCLE ORDER BUGS
-------------------------------
- THE MESSY REALITY: Plugins must unload in reverse order of loading, but each plugin
  assumed it was last.
- THE SOLUTION: The host guarantees order; plugin authors don't have to care.

PROBLEM 3: ADDING PLATFORM-WIDE FEATURES
----------------------------------------
- THE MESSY REALITY: You want per-hook timing and tracing. You'd have to edit every plugin.
- THE SOLUTION: Wrap the single call site in PluginHost._safe().

PROBLEM 4: SIMPLE PLUGIN AUTHORING
----------------------------------
- THE MESSY REALITY: Plugin authors must learn the host's internal API surface.
- THE SOLUTION: They override only the hooks they care about.
"""

if __name__ == "__main__":
    print("--- Plugin Host ---")
    host = PluginHost()
    metrics = MetricsPlugin()
    for p in (AuditPlugin(), BrokenPlugin(), metrics):
        host.register(p)
    host.start()
    host.dispatch("user_login", {"user": "ada"})
    host.stop()
    print("Host recorded errors:", host.errors)

    print("\n--- Decorator Hooks ---")
    app = MiniApp()

    @app.on("greet")
    def greet(payload):
        return f"Hello {payload['name']}"

    print(app.emit("greet", {"name": "Ada"}))
