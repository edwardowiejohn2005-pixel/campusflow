"""Assignment, status lifecycle and the work queue (Engineer B)."""

from .errors import InvalidTransitionError, ValidationError
from .tickets import PRIORITIES, find_ticket, ticket_number

# Allowed forward moves. Reopening is a separate, explicit action.
_ALLOWED = {
    "open": {"in_progress"},
    "in_progress": {"resolved"},
    "resolved": set(),
}


def assign_ticket(tickets, ticket_id, staff_name):
    """Assign a ticket to a non-empty staff name and return the ticket."""
    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValidationError("Staff member name must not be blank.")
    ticket = find_ticket(tickets, ticket_id)
    if ticket["status"] == "resolved":
        raise InvalidTransitionError(
            f"{ticket['id']} is resolved. Reopen it before changing it."
        )
    ticket["assigned_to"] = staff_name.strip()
    return ticket


def change_status(tickets, ticket_id, new_status):
    """Move a ticket forward: open -> in_progress -> resolved."""
    if not isinstance(new_status, str):
        raise InvalidTransitionError("Status must be text.")
    target = new_status.strip().lower()
    ticket = find_ticket(tickets, ticket_id)
    current = ticket["status"]

    if target not in _ALLOWED:
        raise InvalidTransitionError(
            f"Unknown status {new_status!r}. Use open, in_progress or resolved "
            "(use reopen_ticket to reopen)."
        )
    if target not in _ALLOWED[current]:
        raise InvalidTransitionError(
            f"Cannot move {ticket['id']} from {current} to {target}."
        )
    if target == "in_progress" and not ticket["assigned_to"]:
        raise InvalidTransitionError(
            f"{ticket['id']} is unassigned; assign it before starting work."
        )
    ticket["status"] = target
    return ticket


def reopen_ticket(tickets, ticket_id):
    """Explicitly reopen a resolved ticket (sets status back to open)."""
    ticket = find_ticket(tickets, ticket_id)
    if ticket["status"] != "resolved":
        raise InvalidTransitionError(
            f"{ticket['id']} is {ticket['status']}; only resolved tickets can be reopened."
        )
    ticket["status"] = "open"
    return ticket


def work_queue(tickets):
    """Open tickets ordered critical -> low, ties broken by earlier numeric ID.

    Only tickets whose status is ``open`` are included, per the spec
    ("open, unresolved tickets").
    """
    rank = {name: index for index, name in enumerate(PRIORITIES)}
    open_tickets = [t for t in tickets if t["status"] == "open"]
    return sorted(
        open_tickets,
        key=lambda t: (rank[t["priority"]], ticket_number(t["id"])),
    )
