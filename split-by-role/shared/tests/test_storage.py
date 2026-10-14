import os
import tempfile
import unittest

from campusflow.cli import run
from campusflow.errors import StorageError
from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import create_ticket


class StorageTests(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._dir.cleanup)
        self.path = os.path.join(self._dir.name, "data", "tickets.json")

    def test_missing_file_gives_fresh_start(self):
        self.assertEqual(load_tickets(self.path), [])

    def test_save_and_reload_preserves_tickets(self):
        tickets = []
        create_ticket(tickets, "Wi-Fi down", "Network", "high", 12)
        create_ticket(tickets, "Laptop", "Hardware", "low", 1)
        tickets[1]["assigned_to"] = "Amina"
        save_tickets(tickets, self.path)
        self.assertEqual(load_tickets(self.path), tickets)

    def test_create_after_reload_does_not_duplicate_ids(self):
        tickets = []
        create_ticket(tickets, "one", "Other", "low", 1)
        create_ticket(tickets, "two", "Other", "low", 1)
        save_tickets(tickets, self.path)
        reloaded = load_tickets(self.path)
        new_ticket = create_ticket(reloaded, "three", "Other", "low", 1)
        self.assertEqual(new_ticket["id"], "T003")
        ids = [t["id"] for t in reloaded]
        self.assertEqual(len(ids), len(set(ids)))

    def test_corrupted_json_raises_and_file_is_untouched(self):
        os.makedirs(os.path.dirname(self.path))
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write("{not valid json")
        with self.assertRaises(StorageError):
            load_tickets(self.path)
        with open(self.path, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), "{not valid json")

    def test_wrong_shape_raises(self):
        os.makedirs(os.path.dirname(self.path))
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write('{"id": "T001"}')
        with self.assertRaises(StorageError):
            load_tickets(self.path)
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write('[{"id": "T001"}]')
        with self.assertRaises(StorageError):
            load_tickets(self.path)


class CliTests(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._dir.cleanup)
        self.path = os.path.join(self._dir.name, "tickets.json")

    def drive(self, *answers):
        """Run the menu with scripted answers; return (exit_code, output)."""
        feed = iter(answers)
        lines = []
        code = run(self.path, input_fn=lambda prompt="": next(feed), output_fn=lines.append)
        return code, "\n".join(lines)

    def test_full_session_survives_restart(self):
        code, out = self.drive(
            "1", "Wi-Fi down", "network", "high", "15",
            "1", "Bad ticket", "Network", "low", "0",       # rejected
            "4", "T001", "Amina",
            "5", "T001", "in_progress",
            "5", "T001", "open",                            # invalid transition
            "9",
        )
        self.assertEqual(code, 0)
        self.assertIn("Created T001 with priority critical", out)
        self.assertIn("Error: affected_users must be a positive whole number", out)
        self.assertIn("T001 is now in_progress", out)
        self.assertIn("Error: Cannot move T001 from in_progress to open", out)

        # Second run: data reloaded, new ticket gets a fresh ID.
        code, out = self.drive("2", "1", "Printer", "Hardware", "low", "1", "7", "8", "9")
        self.assertEqual(code, 0)
        self.assertIn("Wi-Fi down", out)
        self.assertIn("Created T002 with priority low", out)
        self.assertIn("Total tickets: 2", out)

    def test_bad_json_stops_startup_without_overwriting(self):
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write("garbage")
        code, out = self.drive("9")
        self.assertEqual(code, 1)
        self.assertIn("invalid JSON", out)
        with open(self.path, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), "garbage")

    def test_invalid_menu_choice_and_empty_views(self):
        code, out = self.drive("x", "2", "7", "8", "3", "T001", "9")
        self.assertEqual(code, 0)
        self.assertIn("Invalid choice", out)
        self.assertIn("No tickets yet.", out)
        self.assertIn("The work queue is empty.", out)
        self.assertIn("Total tickets: 0", out)
        self.assertIn("Error: No ticket with ID 'T001'", out)


if __name__ == "__main__":
    unittest.main()
