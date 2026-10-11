"""
================================================================================
1. BAD CODE: THE REPORT SERVICE WELDED TO ONE STORAGE VENDOR
================================================================================
CRITIQUE: ReportService instantiates a specific disk class and calls its
vendor-specific methods, so moving to cloud storage means rewriting the service.
"""

class LocalDisk:
    def __init__(self): self.files = {}
    def write_file_to_disk(self, path: str, data: str) -> None:
        self.files[path] = data
    def read_file_from_disk(self, path: str) -> str:
        return self.files[path]


class BadReportService:
    def __init__(self):
        self.disk = LocalDisk()  # ❌ Hardwired to a concrete class

    def publish(self, name: str, body: str) -> None:
        # ❌ Uses the implementation's private vocabulary
        self.disk.write_file_to_disk(f"/var/reports/{name}.txt", body)


"""
================================================================================
2. THE PRINCIPLE: "PROGRAM TO INTERFACES, NOT IMPLEMENTATIONS"
================================================================================
What Varies:
    WHERE and HOW files are stored: local disk, S3, Azure Blob, an in-memory fake.

What Stays Stable:
    The business operation: "save this named document" and "load it back."
"""


"""
================================================================================
3. GOOD CODE: THE SERVICE DEPENDS ON A STORAGE CONTRACT
================================================================================
"""
from abc import ABC, abstractmethod

# ------------------------------------------------------------------------------
# APPROACH A: ABSTRACT INTERFACE + INTERCHANGEABLE IMPLEMENTATIONS
# ------------------------------------------------------------------------------

class FileStorage(ABC):
    """The Immutable Boundary the service talks to."""
    @abstractmethod
    def save(self, name: str, content: str) -> None: ...

    @abstractmethod
    def load(self, name: str) -> str: ...


class LocalDiskStorage(FileStorage):
    def __init__(self): self._files = {}
    def save(self, name: str, content: str) -> None:
        print(f"[Disk] writing /var/reports/{name}.txt")
        self._files[name] = content
    def load(self, name: str) -> str:
        return self._files[name]


class CloudBucketStorage(FileStorage):
    def __init__(self, bucket: str):
        self._bucket = bucket
        self._objects = {}
    def save(self, name: str, content: str) -> None:
        print(f"[Cloud] PUT s3://{self._bucket}/{name}")
        self._objects[name] = content
    def load(self, name: str) -> str:
        return self._objects[name]


class ReportService:
    def __init__(self, storage: FileStorage):
        self._storage = storage

    def publish(self, name: str, body: str) -> None:
        self._storage.save(name, body.strip())

    def read(self, name: str) -> str:
        return self._storage.load(name)


# ------------------------------------------------------------------------------
# APPROACH B: A TEST DOUBLE THAT FULFILS THE SAME INTERFACE
# ------------------------------------------------------------------------------

class FakeStorage(FileStorage):
    def __init__(self): self.saved = {}
    def save(self, name: str, content: str) -> None: self.saved[name] = content
    def load(self, name: str) -> str: return self.saved[name]


"""
================================================================================
4. WHAT IT SOLVES IN REALITY: MONETARY AND PRODUCTION BREAKDOWN
================================================================================

PROBLEM 1: CLOUD MIGRATION
--------------------------
- THE MESSY REALITY: Leadership decides to leave the data center. Every class that calls
  write_file_to_disk() must be found and rewritten: weeks of work, high regression risk.
- THE SOLUTION: Write CloudBucketStorage once, pass it to ReportService. Zero edits to
  business logic.

PROBLEM 2: SLOW, FLAKY TESTS
----------------------------
- THE MESSY REALITY: Tests touch a real disk or bucket, so they're slow and fail when
  the network hiccups.
- THE SOLUTION: Inject FakeStorage. Tests run in milliseconds and never leave memory.

PROBLEM 3: PARALLEL TEAM WORK
-----------------------------
- THE MESSY REALITY: The platform team builds the cloud adapter while the product team
  builds reports, but neither can start until the other finishes.
- THE SOLUTION: Both agree on FileStorage first, then work independently.

PROBLEM 4: PER-CUSTOMER STORAGE POLICIES
----------------------------------------
- THE MESSY REALITY: EU customers' data must stay in EU buckets. In the bad design that
  means if/else on region inside the service.
- THE SOLUTION: Build ReportService(CloudBucketStorage("eu-bucket")) per region.
"""

if __name__ == "__main__":
    print("--- Local Disk ---")
    svc = ReportService(LocalDiskStorage())
    svc.publish("q3", "  Revenue is up  ")
    print(svc.read("q3"))

    print("\n--- Swapped to Cloud (no service changes) ---")
    svc = ReportService(CloudBucketStorage("eu-reports"))
    svc.publish("q3", "Revenue is up")
    print(svc.read("q3"))

    print("\n--- With Fake (tests) ---")
    fake = FakeStorage()
    ReportService(fake).publish("t", " x ")
    print(fake.saved)
