
import unittest

from campusflow.tickets import create_ticket
from campusflow.notes import add_note
from campusflow.workflow import (
    assign_ticket,
    change_status,
    reopen_ticket,
)
from campusflow.errors import InvalidTransitionError, ValidationError


class NoteTests(unittest.TestCase):

    def setUp(self):
        self.tickets = []
        create_ticket(
            self.tickets,
            "Wi-Fi not working",
            "Network",
            "high",
            12,
        )

    def test_valid_note(self):
        note = add_note(
            self.tickets,
            "T001",
            "Engineer A",
            "Router checked",
        )

        self.assertEqual(note["note_id"], "N001")
        self.assertEqual(len(self.tickets[0]["notes"]), 1)

    def test_short_note_rejected(self):
        with self.assertRaises(ValidationError):
            add_note(self.tickets, "T001", "Engineer A", "Hi")

        self.assertEqual(self.tickets[0]["notes"], [])

        note = add_note(
            self.tickets, "T001", "Engineer A", "Valid note"
        )
        self.assertEqual(note["note_id"], "N001")

    def test_resolved_ticket_rejects_note(self):
        assign_ticket(self.tickets, "T001", "Engineer A")
        change_status(self.tickets, "T001", "in_progress")
        change_status(self.tickets, "T001", "resolved")

        with self.assertRaises(InvalidTransitionError):
            add_note(
                self.tickets, "T001", "Engineer A", "Another update"
            )

        self.assertEqual(self.tickets[0]["notes"], [])

        reopen_ticket(self.tickets, "T001")

        note = add_note(
            self.tickets, "T001", "Engineer A", "Work restarted"
        )
        self.assertEqual(note["note_id"], "N001")


    def test_in_progress_ticket_accepts_note(self):
        # Assign the ticket before starting work.
        assign_ticket(
            self.tickets,
            "T001",
            "Engineer A"
        )

        # Move ticket to in_progress.
        change_status(
            self.tickets,
            "T001",
            "in_progress"
        )

        # Add a note.
        note = add_note(
            self.tickets,
            "T001",
            "Engineer A",
            "Investigating network connection"
        )

        self.assertEqual(note["note_id"], "N001")
        self.assertEqual(len(self.tickets[0]["notes"]), 1)
        self.assertEqual(
            self.tickets[0]["status"],
            "in_progress"
        )


    def test_unknown_status_rejects_note_without_mutation(self):
        self.tickets[0]["status"] = "completed"

        before = dict(self.tickets[0])

        with self.assertRaises(InvalidTransitionError):
            add_note(
                self.tickets,
                "T001",
                "Engineer A",
                "Checking completed ticket"
            )

        self.assertEqual(self.tickets[0], before)
        self.assertEqual(self.tickets[0]["notes"], [])


if __name__ == "__main__":
    unittest.main()
