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
from .tickets import (
    CATEGORIES,
    URGENCIES,
    PRIORITIES,
    STATUSES,
    calculate_priority,
)
from .tickets import calculate_priority, URGENCIES, PRIORITIES, STATUSES
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
        raise StorageError(
            f"{path} must contain a JSON list of tickets."
        )

    seen_ids = set()

    for index, ticket in enumerate(data):

        # Check required fields.
        if not isinstance(ticket, dict) or any(
            field not in ticket for field in _REQUIRED_FIELDS
        ):
            raise StorageError(
                f"{path}: entry {index + 1} is not a valid ticket."
            )

        # Check ticket ID format.
        ticket_id = ticket["id"]

        if (
            not isinstance(ticket_id, str)
            or not ticket_id.startswith("T")
            or len(ticket_id) < 4
            or not ticket_id[1:].isascii()
            or not ticket_id[1:].isdigit()
            or int(ticket_id[1:]) < 1
        ):
            raise StorageError(
                f"{path}: invalid ticket ID {ticket_id!r}."
            )

        # Reject duplicate ticket IDs.
        if ticket_id in seen_ids:
            raise StorageError(
                f"{path}: duplicate ticket ID {ticket_id}."
            )

        seen_ids.add(ticket_id)


        # Validate urgency before calculating priority.
        urgency = ticket["urgency"]
        affected_users = ticket["affected_users"]
        stored_priority = ticket["priority"]

        if urgency not in URGENCIES or not isinstance(urgency, str):
            raise StorageError(
                f"{path}: invalid urgency for ticket {ticket_id}."
            )

        if type(affected_users) is not int or affected_users < 1:
            raise StorageError(
                f"{path}: invalid affected_users for ticket {ticket_id}."
            )

        if not isinstance(stored_priority, str) or stored_priority not in PRIORITIES:
            raise StorageError(
                f"{path}: invalid priority for ticket {ticket_id}."
            )

        # Compare saved priority with the actual business rule.
        expected_priority = calculate_priority(
            urgency, affected_users
        )

        if stored_priority != expected_priority:
            raise StorageError(
                f"{path}: incorrect priority for {ticket_id}. "
                f"Expected {expected_priority}, got {stored_priority}."
            )

        # Validate the ticket's status.
        status = ticket["status"]

        if not isinstance(status, str) or status not in STATUSES:
            raise StorageError(
                f"{path}: invalid status {status!r} "
                f"for ticket {ticket_id}."
            )

        # Validate ticket category.
        category = ticket["category"]

        if (
            not isinstance(category, str)
            or category not in CATEGORIES
        ):
            raise StorageError(
                f"{path}: invalid category {category!r} "
                f"for ticket {ticket_id}."
            )

        # Validate ticket title.
        title = ticket["title"]

        if (
            not isinstance(title, str)
            or not title.strip()
        ):
            raise StorageError(
                f"{path}: invalid title for ticket {ticket_id}."
            )

        # Validate assigned staff.
        assigned_to = ticket["assigned_to"]

        if assigned_to is not None and (
            not isinstance(assigned_to, str)
            or not assigned_to.strip()
        ):
            raise StorageError(
                f"{path}: invalid assignment "
                f"for ticket {ticket_id}."
            )

        # In-progress tickets must be assigned.
        if status == "in_progress" and assigned_to is None:
            raise StorageError(
                f"{path}: {ticket_id} is in_progress "
                "but has no assigned staff."
            )

        # Validate saved follow-up notes.
        # Existing old tickets may not have a notes field.
        # Give them an empty list for backward compatibility.
        notes = ticket.get("notes", [])

        if not isinstance(notes, list):
            raise StorageError(
                f"{path}: notes for {ticket_id} must be a list."
            )

        seen_note_ids = set()

        for note in notes:
            # A note must be a dictionary.
            if not isinstance(note, dict):
                raise StorageError(
                    f"{path}: invalid note in ticket {ticket_id}."
                )

            # Check required note fields.
            required_note_fields = (
                "note_id", "author", "message"
            )

            if any(
                field not in note
                for field in required_note_fields
            ):
                raise StorageError(
                    f"{path}: note has missing fields "
                    f"in ticket {ticket_id}."
                )

            note_id = note["note_id"]
            author = note["author"]
            message = note["message"]

            # Validate note ID.
            if (
                not isinstance(note_id, str)
                or not note_id.startswith("N")
                or len(note_id) < 4
                or not note_id[1:].isascii()
                or not note_id[1:].isdigit()
                or int(note_id[1:]) < 1
            ):
                raise StorageError(
                    f"{path}: invalid note ID in {ticket_id}."
                )

            # Reject duplicate note IDs within one ticket.
            if note_id in seen_note_ids:
                raise StorageError(
                    f"{path}: duplicate note ID {note_id} "
                    f"in ticket {ticket_id}."
                )

            seen_note_ids.add(note_id)

            # Validate author.
            if (
                not isinstance(author, str)
                or not author.strip()
            ):
                raise StorageError(
                    f"{path}: invalid note author "
                    f"in ticket {ticket_id}."
                )

            # Validate message.
            if (
                not isinstance(message, str)
                or not 5 <= len(message.strip()) <= 300
            ):
                raise StorageError(
                    f"{path}: note message must contain "
                    f"5 to 300 characters in {ticket_id}."
                )

        # Normalize legacy tickets only after validation.
        ticket.setdefault("notes", [])


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
