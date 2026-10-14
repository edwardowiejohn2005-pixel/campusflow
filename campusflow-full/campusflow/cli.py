"""Text menu for CampusFlow.

``run`` takes ``input_fn`` and ``output_fn`` so tests can drive the menu
without a real keyboard.
"""

import sys

from .errors import CampusFlowError, ValidationError
from .reports import build_report, format_report
from .storage import DEFAULT_PATH, load_tickets, save_tickets
from .tickets import (
    CATEGORIES, URGENCIES, create_ticket, find_ticket,
    format_ticket, format_ticket_row,
)
from .workflow import assign_ticket, change_status, reopen_ticket, work_queue

MENU = """
=== CampusFlow Helpdesk ===
1. Create ticket
2. List all tickets
3. View ticket details
4. Assign ticket
5. Change status (open -> in_progress -> resolved)
6. Reopen resolved ticket
7. Work queue
8. Reports
9. Exit
"""

HEADER = f"{'ID':<6} {'PRIORITY':<9} {'STATUS':<12} {'ASSIGNED':<14} TITLE"


def run(path=DEFAULT_PATH, input_fn=input, output_fn=print):
    """Run the menu loop. Returns an exit code (0 ok, 1 on startup error)."""
    try:
        tickets = load_tickets(path)
    except CampusFlowError as exc:
        output_fn(f"Error: {exc}")
        return 1

    def save():
        save_tickets(tickets, path)

    def show_rows(rows, empty_message):
        if not rows:
            output_fn(empty_message)
            return
        output_fn(HEADER)
        for ticket in rows:
            output_fn(format_ticket_row(ticket))

    
    
    def do_create():
        title = input_fn("Title: ")
        category = input_fn(f"Category ({'/'.join(CATEGORIES)}): ")
        urgency = input_fn(f"Urgency ({'/'.join(URGENCIES)}): ")

        users_text = input_fn(
            "Affected users (whole number, 1 or more): "
        ).strip()

        if not (users_text.isascii() and users_text.isdigit()):
            raise ValidationError(
                "affected_users must be a positive whole number (1 or more)."
            )

        users = int(users_text)

        ticket = create_ticket(
            tickets,
            title,
            category,
            urgency,
            users
        )

        try:
            save()
        except CampusFlowError:
            tickets.remove(ticket)
            raise

        output_fn(
            f"Created {ticket['id']} with priority {ticket['priority']}."
        )

    def do_list():
        show_rows(tickets, "No tickets yet.")

    def do_view():
        ticket = find_ticket(tickets, input_fn("Ticket ID: "))
        output_fn(format_ticket(ticket))

    def do_assign():
        ticket_id = input_fn("Ticket ID: ")
        name = input_fn("Assign to (staff name): ")
        ticket = assign_ticket(tickets, ticket_id, name)
        save()
        output_fn(f"{ticket['id']} assigned to {ticket['assigned_to']}.")

    def do_status():
        ticket_id = input_fn("Ticket ID: ")
        new_status = input_fn("New status (in_progress/resolved): ")
        ticket = change_status(tickets, ticket_id, new_status)
        save()
        output_fn(f"{ticket['id']} is now {ticket['status']}.")

    def do_reopen():
        ticket = reopen_ticket(tickets, input_fn("Ticket ID: "))
        save()
        output_fn(f"{ticket['id']} reopened.")

    def do_queue():
        show_rows(work_queue(tickets), "The work queue is empty.")

    def do_report():
        output_fn(format_report(build_report(tickets)))

    actions = {
        "1": do_create, "2": do_list, "3": do_view, "4": do_assign,
        "5": do_status, "6": do_reopen, "7": do_queue, "8": do_report,
    }

    while True:
        output_fn(MENU)
        try:
            choice = input_fn("Choose an option (1-9): ").strip()
        except EOFError:
            output_fn("\nInput closed. Goodbye.")
            return 0
        if choice == "9":
            output_fn("Goodbye.")
            return 0
        action = actions.get(choice)
        if action is None:
            output_fn("Invalid choice. Please enter a number from 1 to 9.")
            continue
        try:
            action()
        except CampusFlowError as exc:
            output_fn(f"Error: {exc}")
        except EOFError:
            output_fn("\nInput closed. Goodbye.")
            return 0


def main():
    sys.exit(run())
