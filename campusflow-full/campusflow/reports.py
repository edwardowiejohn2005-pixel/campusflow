"""Summary reports (Engineer B)."""

from .tickets import PRIORITIES, STATUSES


def build_report(tickets):
    """Return totals and breakdowns. Works for an empty ticket list."""
    by_status = {status: 0 for status in STATUSES}
    by_priority = {priority: 0 for priority in PRIORITIES}
    for ticket in tickets:
        by_status[ticket["status"]] += 1
        by_priority[ticket["priority"]] += 1
    return {
        "total": len(tickets),
        "by_status": by_status,
        "by_priority": by_priority,
    }


def format_report(report):
    lines = [f"Total tickets: {report['total']}", "", "By status:"]
    for status, count in report["by_status"].items():
        lines.append(f"  {status:<12} {count}")
    lines += ["", "By priority:"]
    for priority, count in report["by_priority"].items():
        lines.append(f"  {priority:<12} {count}")
    return "\n".join(lines)
