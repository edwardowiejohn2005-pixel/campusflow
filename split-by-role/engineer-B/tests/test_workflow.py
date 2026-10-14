import unittest

from campusflow.errors import (
    InvalidTransitionError, TicketNotFoundError, ValidationError,
)
from campusflow.reports import build_report, format_report
from campusflow.tickets import create_ticket
from campusflow.workflow import (
    assign_ticket, change_status, reopen_ticket, work_queue,
)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tickets = []
        create_ticket(self.tickets, "Wi-Fi down", "Network", "high", 12)

    def test_unassigned_ticket_cannot_move_to_in_progress(self):
        with self.assertRaises(InvalidTransitionError):
            change_status(self.tickets, "T001", "in_progress")
        self.assertEqual(self.tickets[0]["status"], "open")

    def test_assigned_ticket_progresses_to_resolved(self):
        assign_ticket(self.tickets, "T001", "Amina")
        change_status(self.tickets, "T001", "in_progress")
        self.assertEqual(self.tickets[0]["status"], "in_progress")
        change_status(self.tickets, "T001", "resolved")
        self.assertEqual(self.tickets[0]["status"], "resolved")

    def test_cannot_skip_open_to_resolved(self):
        assign_ticket(self.tickets, "T001", "Amina")
        with self.assertRaises(InvalidTransitionError):
            change_status(self.tickets, "T001", "resolved")
        self.assertEqual(self.tickets[0]["status"], "open")

    def test_unknown_status_rejected(self):
        with self.assertRaises(InvalidTransitionError):
            change_status(self.tickets, "T001", "done")

    def test_assign_rejects_blank_name_and_unknown_id(self):
        with self.assertRaises(ValidationError):
            assign_ticket(self.tickets, "T001", "   ")
        with self.assertRaises(TicketNotFoundError):
            assign_ticket(self.tickets, "T404", "Amina")
        self.assertIsNone(self.tickets[0]["assigned_to"])

    def test_resolved_ticket_locked_until_reopened(self):
        assign_ticket(self.tickets, "T001", "Amina")
        change_status(self.tickets, "T001", "in_progress")
        change_status(self.tickets, "T001", "resolved")
        with self.assertRaises(InvalidTransitionError):
            assign_ticket(self.tickets, "T001", "Bola")
        with self.assertRaises(InvalidTransitionError):
            change_status(self.tickets, "T001", "in_progress")
        self.assertEqual(self.tickets[0]["assigned_to"], "Amina")
        reopen_ticket(self.tickets, "T001")
        self.assertEqual(self.tickets[0]["status"], "open")
        assign_ticket(self.tickets, "T001", "Bola")
        self.assertEqual(self.tickets[0]["assigned_to"], "Bola")

    def test_reopen_only_works_on_resolved(self):
        with self.assertRaises(InvalidTransitionError):
            reopen_ticket(self.tickets, "T001")


class WorkQueueTests(unittest.TestCase):
    def test_queue_sorted_by_priority_then_numeric_id(self):
        tickets = []
        create_ticket(tickets, "a", "Other", "low", 1)       # T001 low
        create_ticket(tickets, "b", "Other", "high", 20)     # T002 critical
        create_ticket(tickets, "c", "Other", "medium", 1)    # T003 medium
        create_ticket(tickets, "d", "Other", "high", 1)      # T004 high
        create_ticket(tickets, "e", "Other", "high", 15)     # T005 critical
        create_ticket(tickets, "f", "Other", "low", 5)       # T006 medium
        order = [t["id"] for t in work_queue(tickets)]
        self.assertEqual(order, ["T002", "T005", "T004", "T003", "T006", "T001"])

    def test_ties_use_numeric_not_text_order(self):
        tickets = [
            {"id": "T010", "priority": "low", "status": "open"},
            {"id": "T002", "priority": "low", "status": "open"},
            {"id": "T1000", "priority": "low", "status": "open"},
        ]
        self.assertEqual([t["id"] for t in work_queue(tickets)], ["T002", "T010", "T1000"])

    def test_queue_excludes_in_progress_and_resolved(self):
        tickets = []
        create_ticket(tickets, "a", "Other", "low", 1)
        create_ticket(tickets, "b", "Other", "low", 1)
        create_ticket(tickets, "c", "Other", "low", 1)
        assign_ticket(tickets, "T002", "Amina")
        change_status(tickets, "T002", "in_progress")
        assign_ticket(tickets, "T003", "Amina")
        change_status(tickets, "T003", "in_progress")
        change_status(tickets, "T003", "resolved")
        self.assertEqual([t["id"] for t in work_queue(tickets)], ["T001"])

    def test_empty_queue(self):
        self.assertEqual(work_queue([]), [])


class ReportTests(unittest.TestCase):
    def test_empty_report_has_zero_counts(self):
        report = build_report([])
        self.assertEqual(report["total"], 0)
        self.assertEqual(sum(report["by_status"].values()), 0)
        self.assertEqual(sum(report["by_priority"].values()), 0)
        self.assertIn("Total tickets: 0", format_report(report))

    def test_report_counts_by_status_and_priority(self):
        tickets = []
        create_ticket(tickets, "a", "Other", "high", 12)  # critical
        create_ticket(tickets, "b", "Other", "low", 1)    # low
        create_ticket(tickets, "c", "Other", "low", 1)    # low
        assign_ticket(tickets, "T002", "Amina")
        change_status(tickets, "T002", "in_progress")
        report = build_report(tickets)
        self.assertEqual(report["total"], 3)
        self.assertEqual(report["by_status"], {"open": 2, "in_progress": 1, "resolved": 0})
        self.assertEqual(report["by_priority"],
                         {"critical": 1, "high": 0, "medium": 0, "low": 2})


if __name__ == "__main__":
    unittest.main()
