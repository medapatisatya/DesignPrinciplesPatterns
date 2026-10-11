# Design Principles Practice Projects (Python)

Hands-on projects to internalize these principles:

1. Encapsulate what varies
2. Favor composition over inheritance
3. Program to interfaces, not implementations
4. Strive for loosely coupled designs
5. Open-Closed Principle (OCP)
6. Dependency Inversion Principle (DIP)
7. Principle of Least Knowledge (Law of Demeter)
8. Hollywood Principle
9. Single Responsibility Principle (SRP)

## Python Toolkit Cheat Sheet

| Need | Use |
|---|---|
| Interface | `abc.ABC` + `@abstractmethod`, or `typing.Protocol` (structural typing) |
| Data holders | `@dataclass` (use `frozen=True` for value objects) |
| Testing | `pytest`, plus `unittest.mock` or hand-written fakes |
| Type checking | `mypy --strict` (it catches many coupling mistakes) |
| Plugin discovery | `importlib`, `pkgutil.iter_modules`, `inspect` |
| Registries | a plain `dict[str, type]`, or a decorator that registers classes |

**Suggested folder layout for every project:**

```
project_name/
├── v1_bad/            # the naive version (where requested)
├── v2_good/           # refactored version
├── tests/
├── NOTES.md           # your write-up (see template at the end)
└── README.md
```

---

## Project 1: Notification System

**Principles:** Encapsulate what varies, Program to interfaces, Loose coupling

### Requirements
- An `AlertService` that sends alerts when events occur (price drop, server down, etc.).
- Channels: Email, SMS, Push, Slack. More must be addable later.
- A user can subscribe to multiple channels and change them at runtime.
- Formatting differs per channel: plain text (SMS, 160 chars max), HTML (Email), JSON (Slack).

### Design hints
- Two things vary independently: **how to format** and **how to send**. Give each its own interface.
- `AlertService` holds a list of channels and loops over them. It must never import or mention `Email`, `SMS`, etc.
- Use a registry or factory (`dict[str, Channel]`) to create channels by name from config.

```python
from abc import ABC, abstractmethod
from typing import Protocol

class Formatter(Protocol):
    def format(self, alert: "Alert") -> str: ...

class Sender(Protocol):
    def send(self, recipient: str, body: str) -> None: ...

# A Channel = Formatter + Sender. AlertService only knows about Channel.
```

### Tasks
- [ ] Define `Alert` (dataclass), `Formatter`, `Sender`, `Channel`.
- [ ] Implement 4 channels (print to console instead of real sending).
- [ ] Implement `subscribe(user, channel)` and `unsubscribe(user, channel)` at runtime.
- [ ] Load a user's channel preferences from a JSON/YAML file.
- [ ] Write tests with a `FakeChannel` that records what it received.

### Self-check
- [ ] Can you add a `WhatsAppChannel` **without opening** `alert_service.py`?
- [ ] Does `grep -i "email\|sms" alert_service.py` return nothing?

### Change request
A client wants "quiet hours": no SMS between 10pm and 7am. Where does this live? (Hint: not in `AlertService`. Try a decorator/wrapper around a `Channel`.)

---

## Project 2: RPG Combat Simulator

**Principles:** Composition over inheritance, Encapsulate what varies, Program to interfaces

### Step 1: The wrong way (inheritance)
Build this hierarchy:

```
Character
├── Warrior
├── Mage
│   └── FireMage
│       └── FlyingFireMage
└── Archer
```

Now add: **FlyingHealer who also uses poison**, **IceMage who walks**, **FlyingArcher**.
Count the new classes needed. Notice duplicated code. Write down how you feel.

### Step 2: The right way (composition)
Characters **have** behaviors instead of **being** types:

```python
class Character:
    def __init__(self, name, hp, attack: AttackBehavior,
                 movement: MovementBehavior, defense: DefenseBehavior):
        ...
```

Behaviors to implement:
- Attack: `SwordSlash`, `Fireball`, `ArrowShot`, `PoisonStrike`, `Heal`
- Movement: `Walk`, `Fly`, `Teleport`
- Defense: `ShieldBlock`, `Dodge`, `NoDefense`

### Step 3: Runtime change
- [ ] Add `character.set_movement(...)`, `set_attack(...)`, `set_defense(...)`.
- [ ] Implement debuffs: "Grounded" swaps `Fly` for `Walk` for 3 turns, then restores the original.
- [ ] Implement a turn-based fight loop between two characters (or two teams).

### Tasks
- [ ] Build v1 (inheritance) and v2 (composition) in separate folders.
- [ ] In v2, create new character types using **only configuration** (a dict or JSON), no new classes.
- [ ] Add a `Stunned` status that replaces attack with `DoNothing`.

### Self-check
- [ ] How many classes did "flying healer with poison" need in v1 vs v2?
- [ ] Can a character gain a new ability mid-fight without a `isinstance` check anywhere?

---

## Project 3: Report Generator

**Principles:** Open-Closed Principle, Single Responsibility Principle

### Requirements
Take sales data (CSV with `date, region, product, quantity, price`) and produce reports.
- Formats: CSV, JSON, HTML, PDF (or a text stand-in)
- Filters: by date range, region, product
- Calculations: total, average, top-N products

### Step 1: The giant class
Write one `ReportManager` that loads data, filters, calculates, formats, saves to disk, and emails. Use `if format == "pdf": ... elif format == "csv": ...` chains.

### Step 2: Find the reasons to change
List every reason `ReportManager` could change. Example: "data source changes", "new format", "new filter", "email provider changes", "new metric". Each reason becomes its own class or module:

- `SalesRepository` (loading data)
- `Filter` interface + implementations
- `Metric` interface + implementations
- `ReportFormatter` interface + implementations
- `ReportWriter` (saving)
- `ReportMailer` (sending)
- `ReportService` (orchestrates only)

### Step 3: OCR test (Open-Closed)
Without editing **any existing file**:
- [ ] Add an `XmlFormatter`.
- [ ] Add a `PriceRangeFilter`.
- [ ] Add a `MedianMetric`.

If you edited an existing file, find out why and refactor. A common fix is auto-registering via a decorator:

```python
FORMATTERS: dict[str, type[ReportFormatter]] = {}

def register(name):
    def wrap(cls):
        FORMATTERS[name] = cls
        return cls
    return wrap

@register("json")
class JsonFormatter(ReportFormatter): ...
```

### Tasks
- [ ] Filters must be **composable**: `DateFilter(...) & RegionFilter(...)` (implement `__and__`).
- [ ] CLI: `python report.py --format xml --region EU --top 5`.
- [ ] Unit test each class in isolation.

### Trade-off to notice
Is a class with one method too small? When does SRP become over-fragmentation?

---

## Project 4: Order Processing with Dependency Injection

**Principles:** Dependency Inversion, Loose coupling, Program to interfaces

### Requirements
`OrderService.place_order(order)` must: check inventory, charge payment, reserve stock, and send a confirmation.

### Step 1: Tightly coupled v1
```python
class OrderService:
    def __init__(self):
        self.payment = StripePayment()       # concrete!
        self.inventory = PostgresInventory() # concrete!
        self.notifier = SmtpEmailer()        # concrete!
```
Now try to write a unit test for it. Notice you can't, without hitting real services.

### Step 2: Inverted v2
Define abstractions **owned by the high-level module** (`OrderService`'s package):

```python
class PaymentGateway(Protocol):
    def charge(self, amount: Decimal, token: str) -> PaymentResult: ...

class InventoryRepo(Protocol):
    def is_available(self, sku: str, qty: int) -> bool: ...
    def reserve(self, sku: str, qty: int) -> None: ...

class Notifier(Protocol):
    def notify(self, user_id: str, message: str) -> None: ...
```

Inject via constructor. Provide real-ish implementations (`StripeGateway`, `SqliteInventory`, `EmailNotifier`) **and** fakes (`FakeGateway`, `InMemoryInventory`, `SpyNotifier`).

### Tasks
- [ ] Write pytest tests: success path, out-of-stock, payment declined, payment gateway raises exception.
- [ ] Verify the declined-payment test does **not** reserve stock (or rolls it back).
- [ ] Switch from Stripe to PayPal by changing **only the wiring**.
- [ ] Bonus: write a tiny container.

```python
class Container:
    def __init__(self):
        self._factories = {}
    def register(self, iface, factory): self._factories[iface] = factory
    def resolve(self, iface): return self._factories[iface](self)
```

- [ ] Bonus 2: add a `composition_root.py` (the only file allowed to import concrete classes).

### Self-check
- [ ] Does `order_service.py` import anything from `stripe`, `sqlite3`, or `smtplib`? It shouldn't.
- [ ] Do your tests run in milliseconds with zero network?

---

## Project 5: Smart Home Controller

**Principles:** Law of Demeter, Loose coupling, Encapsulation

### Model
`House → Room → Device (Light, Blind, TV, Thermostat) → Settings`

### Step 1: Train-wreck code
```python
house.get_room("kitchen").get_light().get_bulb().set_brightness(50)
house.get_room("living").get_tv().get_settings().set_volume(10)
```

### Step 2: Refactor
Callers talk only to their direct collaborator:

```python
house.dim("kitchen", 50)
room.dim(50)           # Room delegates to its own light
tv.set_volume(10)
```

### Step 3: Scenes
- [ ] Implement `Scene` (Movie Mode: dim lights to 10%, close blinds, TV on, volume 15).
- [ ] The client calls `house.activate_scene("movie")` and knows nothing about lights/blinds/TV.
- [ ] Bonus: scenes are defined as data (JSON) so adding "Sleep Mode" needs no code.

### Self-check
- [ ] Run: `grep -nE "\w+\.\w+\(.*\)\.\w+\(" **/*.py` and justify each hit. (Fluent builders and `str.strip().lower()` chains are fine; chains through domain objects are not.)
- [ ] Did `Room` or `House` get 30 delegating methods? That's the cost of Demeter. Could a `Scene` or `Command` object reduce it?

---

## Project 6: Mini Framework (Hollywood Principle)

**Principle:** "Don't call us, we'll call you."

### Part A: Template Method
```python
class DataImporter(ABC):
    def run(self):                    # fixed algorithm, framework owns it
        raw = self.read_source()
        records = self.parse(raw)
        valid = [r for r in records if self.validate(r)]
        self.save(valid)
        self.on_complete(len(valid))  # optional hook, default no-op

    @abstractmethod
    def read_source(self): ...
    @abstractmethod
    def parse(self, raw): ...
    def validate(self, record) -> bool: return True
    @abstractmethod
    def save(self, records): ...
    def on_complete(self, count): pass
```
- [ ] Implement `CsvImporter`, `JsonImporter`, `ApiImporter`.
- [ ] Subclasses must never call `run()` steps in their own order.

### Part B: Event Bus
- [ ] Build `EventBus` with `subscribe(event_name, callback)`, `publish(event_name, payload)`.
- [ ] Components register handlers (`on_order_placed`, `on_user_signup`). The bus invokes them.
- [ ] Handle: multiple subscribers, unsubscribe, a handler raising an exception (should not break others).
- [ ] Bonus: priority ordering and async handlers.

### Part C: Plugin Loader
- [ ] App scans a `plugins/` folder, imports each module, and finds classes subclassing `Plugin`.
- [ ] The app calls `plugin.init(context)` at startup and `plugin.execute()` when triggered.
- [ ] Drop a new `.py` file into `plugins/` and it works with **no change** to the app.

```python
import importlib, pkgutil, inspect

def discover(package):
    for _, name, _ in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{package.__name__}.{name}")
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls, Plugin) and cls is not Plugin:
                yield cls
```

### Self-check
- [ ] In your plugin code, is there any place where **you** call the framework's lifecycle? There shouldn't be. You only implement hooks.
- [ ] Which Python frameworks do this? (Django signals, Flask `@app.route`, pytest fixtures and hooks, Tkinter callbacks.)

---

## Capstone: Online Food Delivery Backend

Combine everything into one system.

### Domain
Customers, Restaurants, Menu items, Orders, Delivery partners, Payments, Notifications.

### Feature → Principle map

| Feature | Principle(s) |
|---|---|
| Pluggable pricing rules: surge, coupon, loyalty discount, delivery fee | Encapsulate what varies, OCP |
| Delivery assignment: nearest, least busy, highest rated | Composition, interfaces (Strategy) |
| `OrderService` depends on `PaymentGateway`, `Notifier`, `DeliveryAssigner`, `OrderRepo` | DIP, loose coupling |
| Order lifecycle hooks: `on_placed`, `on_accepted`, `on_picked_up`, `on_delivered` | Hollywood |
| Order state machine (Placed → Accepted → Picked → Delivered / Cancelled) | Encapsulate what varies |
| Clean calls (`order.assign(partner)`, not `order.get_restaurant().get_owner().get_phone()`) | Law of Demeter |
| Each class has one job: `PriceCalculator`, `OrderValidator`, `OrderRepo`, `OrderService` | SRP |

### Tasks
- [ ] Define interfaces first (`Protocol`s), then implementations.
- [ ] Pricing: a `PricingRule` chain where each rule adjusts the running total. Order of rules should be configurable.
- [ ] Delivery assignment: a `DeliveryStrategy` swappable at runtime (e.g., switch to "nearest" during rush hour).
- [ ] An `EventBus` that fires lifecycle events; `Notifier`, `Analytics`, `LoyaltyPoints` subscribe independently.
- [ ] Single `composition_root.py` that wires everything.
- [ ] Tests: `OrderService` fully tested with fakes. Aim for 90%+ coverage on the domain layer.
- [ ] CLI or small FastAPI layer on top (optional).

### Change requests (do these last; count files touched)
1. Add a "festival discount" pricing rule. **Target: 1 new file, 0 edits** (plus one wiring line).
2. Add a "highest rated partner" assignment strategy. **Target: 1 new file.**
3. Add an SMS notification when an order is delivered. **Target: 1 new file + wiring.**
4. Replace the in-memory repo with SQLite. **Target: 1 new file + wiring.**

---

## Tips for Maximum Learning

1. **Write the bad version first** (Projects 2, 3, 4, 5). Feeling the pain makes the principle stick.
2. **Always do the change request** after finishing. Count the existing files you had to modify. The goal is zero.
3. **Run `mypy --strict`**. Mismatched interfaces show up immediately.
4. **Don't over-engineer.** Python is dynamic; not every function needs a class. Use a function where a one-method class would be silly (a `Callable` is a perfectly good Strategy).
5. **Notice principle conflicts:**
   - Demeter produces many thin wrapper methods.
   - SRP can over-fragment code into tiny classes.
   - OCP's abstractions cost readability if there is only ever one implementation.
   - Ask: *"Does this part actually vary?"* If not, keep it simple.

## NOTES.md Template (one per project)

```markdown
# Project N: <name>

## Principles applied
- <principle>: where in code, and why

## What would break without it
- <concrete scenario, e.g. "adding WhatsApp would require editing AlertService">

## Change request results
- Request: ...
- Files edited: N  | New files: M

## Trade-offs / things that felt awkward
- ...

## What I'd do differently
- ...
```

## Suggested Order and Time

| # | Project | Est. time |
|---|---|---|
| 1 | Notification System | 3-4 hrs |
| 2 | RPG Combat Simulator | 4-5 hrs |
| 3 | Report Generator | 4-6 hrs |
| 4 | Order Processing + DI | 4-5 hrs |
| 5 | Smart Home Controller | 2-3 hrs |
| 6 | Mini Framework | 5-6 hrs |
| ★ | Capstone | 1-2 weekends |
