
"""Structured follow-up notes for CampusFlow tickets."""

from .errors import InvalidTransitionError, ValidationError
from .tickets import find_ticket


def add_note(tickets, ticket_id, author, message):
    """Add a note without modifying data when validation fails."""

    ticket = find_ticket(tickets, ticket_id)

    if ticket["status"] not in ("open", "in_progress"):
        raise InvalidTransitionError(
            "Notes can only be added to open or in_progress tickets."
        )

    if not isinstance(author, str) or not author.strip():
        raise ValidationError("Note author cannot be blank.")

    if not isinstance(message, str):
        raise ValidationError("Note message must be text.")

    clean_message = message.strip()

    if not 5 <= len(clean_message) <= 300:
        raise ValidationError(
            "Note message must contain 5 to 300 characters."
        )

    existing_notes = ticket.get("notes", [])

    if not isinstance(existing_notes, list):
        raise ValidationError("Invalid ticket notes collection.")

    # Determine the next available ID without changing stored data.
    numbers = []
    for existing in existing_notes:
        if not isinstance(existing, dict):
            raise ValidationError("Invalid existing note.")

        note_id = existing.get("note_id")
        if (
            not isinstance(note_id, str)
            or not note_id.startswith("N")
            or not note_id[1:].isascii()
            or not note_id[1:].isdigit()
            or len(note_id) < 4
            or int(note_id[1:]) < 1
        ):
            raise ValidationError("Invalid existing note ID.")

        numbers.append(int(note_id[1:]))

    if len(numbers) != len(set(numbers)):
        raise ValidationError("Duplicate existing note IDs.")

    next_number = max(numbers, default=0) + 1

    note = {
        "note_id": f"N{next_number:03d}",
        "author": author.strip(),
        "message": clean_message,
    }

    ticket["notes"] = existing_notes + [note]

    return note
