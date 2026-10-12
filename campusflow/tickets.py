"""Ticket creation, validation, and the priority engine (Engineer A).

Tickets are plain dictionaries stored in a list that callers pass in.
"""

from .errors import TicketNotFoundError, ValidationError

CATEGORIES = ("Network", "Hardware", "Software", "Other")
URGENCIES = ("low", "medium", "high")
PRIORITIES = ("critical", "high", "medium", "low")
STATUSES = ("open", "in_progress", "resolved")


def calculate_priority(urgency, affected_users):
    """Apply the four priority rules in order; the first match wins."""
    if urgency == "high" and affected_users >= 10:
        return "critical"
    if urgency == "high" or affected_users >= 10:
        return "high"
    if urgency == "medium" or affected_users >= 3:
        return "medium"
    return "low"


def normalize_title(title):
    if not isinstance(title, str) or not title.strip():
        raise ValidationError("Title must not be blank.")
    return title.strip()


def normalize_category(category):
    if isinstance(category, str):
        for allowed in CATEGORIES:
            if category.strip().lower() == allowed.lower():
                return allowed
    raise ValidationError(
        f"Invalid category {category!r}. Choose one of: {', '.join(CATEGORIES)}."
    )


def normalize_urgency(urgency):
    if isinstance(urgency, str) and urgency.strip().lower() in URGENCIES:
        return urgency.strip().lower()
    raise ValidationError(
        f"Invalid urgency {urgency!r}. Choose one of: {', '.join(URGENCIES)}."
    )


def normalize_affected_users(value):
    """Return a positive int, or raise ValidationError.

    Rejects zero, negatives, decimals, booleans and non-numeric text.
    """
    message = "affected_users must be a positive whole number (1 or more)."
    if isinstance(value, bool):
        raise ValidationError(message)
    if isinstance(value, int):
        number = value
    elif isinstance(value, str):
        text = value.strip()
        if not (text.isascii() and text.isdigit()):  # rejects '-3', '2.5', 'abc', '', '²'
            raise ValidationError(message)
        number = int(text)
    else:
        raise ValidationError(message)
    if number < 1:
        raise ValidationError(message)
    return number


def ticket_number(ticket_id):
    """Numeric part of an ID: 'T012' -> 12."""
    return int(str(ticket_id)[1:])


def next_ticket_id(tickets):
    """Next unique ID based on the highest number present (safe after reload)."""
    highest = 0
    for ticket in tickets:
        try:
            highest = max(highest, ticket_number(ticket["id"]))
        except (ValueError, KeyError, TypeError):
            continue
    return f"T{highest + 1:03d}"


def create_ticket(tickets, title, category, urgency, affected_users):
    """Validate input, build a ticket, append it to ``tickets`` and return it.

    Nothing is appended if validation fails, so stored data is never corrupted.
    """
    clean_title = normalize_title(title)
    clean_category = normalize_category(category)
    clean_urgency = normalize_urgency(urgency)
    clean_users = normalize_affected_users(affected_users)

    ticket = {
        "id": next_ticket_id(tickets),
        "title": clean_title,
        "category": clean_category,
        "urgency": clean_urgency,
        "affected_users": clean_users,
        "priority": calculate_priority(clean_urgency, clean_users),
        "status": "open",
        "assigned_to": None,
    }
    tickets.append(ticket)
    return ticket


def find_ticket(tickets, ticket_id):
    """Return the ticket with this ID (case-insensitive) or raise."""
    wanted = str(ticket_id).strip().upper()
    for ticket in tickets:
        if ticket["id"] == wanted:
            return ticket
    raise TicketNotFoundError(f"No ticket with ID {str(ticket_id).strip()!r}.")


def format_ticket(ticket):
    """Multi-line detail view of one ticket."""
    assigned = ticket["assigned_to"] or "(unassigned)"
    return (
        f"ID:             {ticket['id']}\n"
        f"Title:          {ticket['title']}\n"
        f"Category:       {ticket['category']}\n"
        f"Urgency:        {ticket['urgency']}\n"
        f"Affected users: {ticket['affected_users']}\n"
        f"Priority:       {ticket['priority']}\n"
        f"Status:         {ticket['status']}\n"
        f"Assigned to:    {assigned}"
    )


def format_ticket_row(ticket):
    """One-line summary used in lists and the work queue."""
    assigned = ticket["assigned_to"] or "-"
    return (
        f"{ticket['id']:<6} {ticket['priority']:<9} {ticket['status']:<12} "
        f"{assigned:<14} {ticket['title']}"
    )
