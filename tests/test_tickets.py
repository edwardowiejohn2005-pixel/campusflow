import unittest

from campusflow.errors import TicketNotFoundError, ValidationError
from campusflow.tickets import (
    calculate_priority, create_ticket, find_ticket, next_ticket_id,
)


class PriorityEngineTests(unittest.TestCase):
    def test_high_urgency_12_users_is_critical(self):
        self.assertEqual(calculate_priority("high", 12), "critical")

    def test_high_urgency_2_users_is_high(self):
        self.assertEqual(calculate_priority("high", 2), "high")

    def test_low_urgency_4_users_is_medium(self):
        self.assertEqual(calculate_priority("low", 4), "medium")

    def test_low_urgency_1_user_is_low(self):
        self.assertEqual(calculate_priority("low", 1), "low")

    def test_boundaries(self):
        self.assertEqual(calculate_priority("high", 10), "critical")
        self.assertEqual(calculate_priority("medium", 10), "high")
        self.assertEqual(calculate_priority("low", 10), "high")
        self.assertEqual(calculate_priority("low", 9), "medium")
        self.assertEqual(calculate_priority("low", 3), "medium")
        self.assertEqual(calculate_priority("low", 2), "low")
        self.assertEqual(calculate_priority("medium", 1), "medium")


class CreateTicketTests(unittest.TestCase):
    def setUp(self):
        self.tickets = []

    def test_create_valid_ticket_has_all_fields(self):
        ticket = create_ticket(self.tickets, "Campus Wi-Fi is down", "Network", "high", 15)
        self.assertEqual(ticket, {
            "id": "T001",
            "title": "Campus Wi-Fi is down",
            "category": "Network",
            "urgency": "high",
            "affected_users": 15,
            "priority": "critical",
            "status": "open",
            "assigned_to": None,
        })
        self.assertEqual(self.tickets, [ticket])

    def test_ids_are_sequential_and_unique(self):
        for _ in range(3):
            create_ticket(self.tickets, "Issue", "Other", "low", 1)
        self.assertEqual([t["id"] for t in self.tickets], ["T001", "T002", "T003"])

    def test_case_variations_are_normalized(self):
        ticket = create_ticket(self.tickets, "  Broken laptop ", "hARDWARE", " HIGH ", " 5 ")
        self.assertEqual(ticket["title"], "Broken laptop")
        self.assertEqual(ticket["category"], "Hardware")
        self.assertEqual(ticket["urgency"], "high")
        self.assertEqual(ticket["affected_users"], 5)

    def test_zero_affected_users_rejected(self):
        with self.assertRaises(ValidationError):
            create_ticket(self.tickets, "Issue", "Network", "low", 0)
        self.assertEqual(self.tickets, [])

    def test_invalid_affected_users_rejected(self):
        for bad in (-1, "-3", "2.5", 2.5, "abc", "", None, True):
            with self.subTest(value=bad):
                with self.assertRaises(ValidationError):
                    create_ticket(self.tickets, "Issue", "Network", "low", bad)
        self.assertEqual(self.tickets, [])

    def test_blank_title_rejected(self):
        for bad in ("", "   ", None):
            with self.subTest(value=bad):
                with self.assertRaises(ValidationError):
                    create_ticket(self.tickets, bad, "Network", "low", 1)
        self.assertEqual(self.tickets, [])

    def test_invalid_category_and_urgency_rejected(self):
        with self.assertRaises(ValidationError):
            create_ticket(self.tickets, "Issue", "Plumbing", "low", 1)
        with self.assertRaises(ValidationError):
            create_ticket(self.tickets, "Issue", "Network", "urgent", 1)
        self.assertEqual(self.tickets, [])

    def test_find_ticket_is_case_insensitive_and_rejects_unknown(self):
        create_ticket(self.tickets, "Issue", "Other", "low", 1)
        self.assertEqual(find_ticket(self.tickets, " t001 ")["id"], "T001")
        with self.assertRaises(TicketNotFoundError):
            find_ticket(self.tickets, "T999")

    def test_next_id_does_not_reuse_numbers_with_gaps(self):
        tickets = [{"id": "T001"}, {"id": "T005"}]
        self.assertEqual(next_ticket_id(tickets), "T006")


if __name__ == "__main__":
    unittest.main()
