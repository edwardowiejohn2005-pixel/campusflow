"""JSON persistence (shared module).

Rules:
* A missing file means a fresh start (empty list).
* A malformed or wrongly-shaped file raises StorageError. We never overwrite
  or erase it silently.
* Saves are atomic (write temp file, then replace) so a crash cannot leave a
  half-written file.
"""

import json
import os
import tempfile

from .errors import StorageError

DEFAULT_PATH = os.path.join("data", "tickets.json")

_REQUIRED_FIELDS = (
    "id", "title", "category", "urgency",
    "affected_users", "priority", "status", "assigned_to",
)


def load_tickets(path=DEFAULT_PATH):
    """Return the list of tickets stored at ``path``."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as exc:
        raise StorageError(
            f"{path} contains invalid JSON ({exc}). Fix or move the file; "
            "it has NOT been changed."
        ) from exc
    except OSError as exc:
        raise StorageError(f"Could not read {path}: {exc}") from exc

    if not isinstance(data, list):
        raise StorageError(f"{path} must contain a JSON list of tickets.")
    for index, ticket in enumerate(data):
        if not isinstance(ticket, dict) or any(f not in ticket for f in _REQUIRED_FIELDS):
            raise StorageError(
                f"{path}: entry {index + 1} is not a valid ticket. "
                "The file has NOT been changed."
            )
    return data


def save_tickets(tickets, path=DEFAULT_PATH):
    """Atomically write ``tickets`` to ``path`` as JSON."""
    directory = os.path.dirname(path) or "."
    temp_name = None
    try:
        os.makedirs(directory, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(dir=directory, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(tickets, handle, indent=2)
        os.replace(temp_name, path)
    except OSError as exc:
        if temp_name and os.path.exists(temp_name):
            os.remove(temp_name)
        raise StorageError(f"Could not save to {path}: {exc}") from exc
