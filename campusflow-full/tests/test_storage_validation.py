
import json
import tempfile
import unittest
from pathlib import Path
from copy import deepcopy

from campusflow.errors import StorageError
from campusflow.storage import load_tickets
from campusflow.tickets import create_ticket
from campusflow.notes import add_note
from campusflow.storage import save_tickets


class StorageValidationTests(unittest.TestCase):

    def test_duplicate_ticket_ids_rejected(self):
        tickets = []

        create_ticket(
            tickets,
            "Wi-Fi problem",
            "Network",
            "high",
            12
        )

        # Duplicate the same ticket ID.
        duplicate = tickets[0].copy()
        tickets.append(duplicate)

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"

            with open(path, "w", encoding="utf-8") as file:
                json.dump(tickets, file)

            with self.assertRaises(StorageError):
                load_tickets(path)

    def test_incorrect_priority_rejected(self):
        tickets = []

        create_ticket(
            tickets,
            "Campus internet down",
            "Network",
            "high",
            15
        )

        # Deliberately corrupt the calculated priority.
        tickets[0]["priority"] = "low"

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"

            with open(path, "w", encoding="utf-8") as file:
                json.dump(tickets, file)

            with self.assertRaises(StorageError):
                load_tickets(path)

    def test_invalid_status_rejected(self):
        tickets = []

        create_ticket(
            tickets,
            "Laptop not working",
            "Hardware",
            "medium",
            3
        )

        # Deliberately introduce an invalid status.
        tickets[0]["status"] = "completed"

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"

            with open(path, "w", encoding="utf-8") as file:
                json.dump(tickets, file)

            with self.assertRaises(StorageError):
                load_tickets(path)


    def test_invalid_saved_note_rejected(self):
        tickets = []

        create_ticket(
            tickets,
            "Laptop problem",
            "Hardware",
            "medium",
            3
        )

        # Add an invalid note directly to the saved data.
        tickets[0]["notes"] = [
            {
                "note_id": "N001",
                "author": "",
                "message": "Hi"
            }
        ]

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"

            with open(path, "w", encoding="utf-8") as file:
                json.dump(tickets, file)

            with self.assertRaises(StorageError):
                load_tickets(path)

    
    def test_notes_preserved_and_ids_continue_after_reload(self):
        tickets = []

        create_ticket(
            tickets,
            "Wi-Fi connection problem",
            "Network",
            "high",
            12
        )

        first_note = add_note(
            tickets, "T001", "Engineer A", "Router checked"
        )

        second_note = add_note(
            tickets, "T001", "Engineer B", "Connection tested"
        )

        self.assertEqual(first_note["note_id"], "N001")
        self.assertEqual(second_note["note_id"], "N002")

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"

            # Save ticket and notes.
            save_tickets(tickets, path)

            # Simulate restarting by loading into a new list.
            reloaded_tickets = load_tickets(path)

            # Check that existing notes survived.
            self.assertEqual(
                reloaded_tickets[0]["notes"],
                tickets[0]["notes"]
            )

            # Add a new note after reloading.
            third_note = add_note(
                reloaded_tickets,
                "T001",
                "Engineer A",
                "Further investigation completed"
            )

            # The next note ID must be N003.
            self.assertEqual(third_note["note_id"], "N003")

            self.assertEqual(
                len(reloaded_tickets[0]["notes"]), 3
            )

    def test_invalid_category_rejected(self):
        tickets = []
        create_ticket(tickets, "Broken laptop", "Hardware", "low", 1)

        tickets[0]["category"] = "Food"

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"
            path.write_text(json.dumps(tickets), encoding="utf-8")

            with self.assertRaises(StorageError):
                load_tickets(path)

    def test_blank_saved_title_rejected(self):
        tickets = []
        create_ticket(tickets, "Network issue", "Network", "high", 5)

        tickets[0]["title"] = "   "

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"
            path.write_text(json.dumps(tickets), encoding="utf-8")

            with self.assertRaises(StorageError):
                load_tickets(path)

    def test_invalid_assignment_rejected(self):
        tickets = []
        create_ticket(tickets, "Software issue", "Software", "low", 1)

        tickets[0]["assigned_to"] = 123

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"
            path.write_text(json.dumps(tickets), encoding="utf-8")

            with self.assertRaises(StorageError):
                load_tickets(path)

    
    def test_duplicate_note_ids_rejected(self):
        tickets = []

        create_ticket(
            tickets,
            "Wi-Fi problem",
            "Network",
            "high",
            12
        )

        tickets[0]["notes"] = [
            {
                "note_id": "N001",
                "author": "Engineer A",
                "message": "Router checked"
            },
            {
                "note_id": "N001",
                "author": "Engineer B",
                "message": "Connection tested"
            }
        ]

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"

            path.write_text(
                json.dumps(tickets),
                encoding="utf-8"
            )

            with self.assertRaises(StorageError):
                load_tickets(path)

    
    def test_failed_load_preserves_existing_tickets(self):
        # Create an existing valid ticket.
        current_tickets = []

        create_ticket(
            current_tickets,
            "Campus Wi-Fi problem",
            "Network",
            "high",
            12
        )

        # Keep a copy to compare later.
        original_tickets = deepcopy(current_tickets)

        # Prepare invalid saved data with duplicate IDs.
        invalid_data = deepcopy(current_tickets)
        invalid_data.append(deepcopy(invalid_data[0]))

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"

            path.write_text(
                json.dumps(invalid_data),
                encoding="utf-8"
            )

            # Simulate replacing the current collection
            # with records loaded from JSON.
            with self.assertRaises(StorageError):
                current_tickets[:] = load_tickets(path)

            # The failed load must preserve existing data.
            self.assertEqual(
                current_tickets,
                original_tickets
            )

            self.assertEqual(len(current_tickets), 1)
            self.assertEqual(current_tickets[0]["id"], "T001")




if __name__ == "__main__":
    unittest.main()
