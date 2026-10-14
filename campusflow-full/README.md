# CampusFlow

A Python command-line helpdesk for Learn2Earn campus staff. It records technical support requests (Wi-Fi outages, faulty laptops, broken dev environments), calculates priority, assigns responsibility, tracks progress, and saves everything to JSON.

**Team:** Engineer A: `<name>` · Engineer B: `<name>`  *(fill in before submitting)*

## Requirements

- Python 3.8 or newer. Standard library only; no packages, database, or API keys.

## Run

```bash
python main.py
```

Tickets are saved to `data/tickets.json` (created automatically, ignored by Git). To start fresh, delete that file.

### Menu

| Option | What it does |
|---|---|
| 1 | Create ticket (validates input, calculates priority, auto-assigns ID `T001`, `T002`, ...) |
| 2 | List all tickets |
| 3 | View one ticket's details |
| 4 | Assign a ticket to a staff member |
| 5 | Change status (`in_progress`, `resolved`) |
| 6 | Reopen a resolved ticket |
| 7 | Work queue (open tickets, most urgent first) |
| 8 | Reports (totals by status and priority) |
| 9 | Exit |

## Test

```bash
python -m unittest discover -s tests -v
```

| File | Covers |
|---|---|
| `tests/test_tickets.py` | Priority rules and boundaries, validation (zero/negative/decimal/text users, blank title, bad category/urgency), ID generation, case normalization |
| `tests/test_workflow.py` | Assignment, lifecycle transitions, reopen, resolved-ticket lock, queue ordering and ties, reports (including empty) |
| `tests/test_storage.py` | JSON round-trip, unique IDs after reload, missing file, corrupted file untouched, wrong-shape file, and scripted end-to-end CLI sessions |

## Rules

**Ticket fields:** `id`, `title`, `category` (Network / Hardware / Software / Other), `urgency` (low / medium / high), `affected_users` (whole number ≥ 1), `priority`, `status`, `assigned_to`. Case variations such as `network` or `HIGH` are accepted and normalized.

**Priority** (first matching rule wins):

1. high urgency **and** 10+ affected users → `critical`
2. high urgency **or** 10+ affected users → `high`
3. medium urgency **or** 3+ affected users → `medium`
4. otherwise → `low`

**Status workflow:** `open → in_progress → resolved`.
- A ticket must be assigned before it can enter `in_progress`.
- Steps cannot be skipped or reversed.
- A resolved ticket cannot be assigned or changed until it is explicitly reopened (menu option 6), which sets it back to `open`.

**Work queue:** tickets with status `open`, ordered critical → high → medium → low; ties broken by the earlier numeric ID (so `T002` comes before `T010`).

**Persistence:** saved after every change. A missing file starts fresh. A malformed or wrongly shaped file stops the program with a clear error and is never overwritten. IDs continue from the highest stored number after reload.

## Project layout

```
main.py                 entry point
campusflow/
  errors.py             shared exceptions
  tickets.py            validation, priority engine, create/find (Engineer A)
  workflow.py           assign, status changes, reopen, work queue (Engineer B)
  reports.py            report totals and formatting (Engineer B)
  storage.py            JSON load/save (shared)
  cli.py                text menu (shared)
tests/                  unittest suites
docs/                   design decisions, AI learning log, sprint kit
```

## Known limitations

- Single-user: no file locking, so two people running it against the same file at once could overwrite each other.
- The work queue shows only `open` tickets. Tickets that are `in_progress` appear in the list and reports but not the queue.
- Staff names are free text (no staff directory); title, category, and urgency cannot be edited after creation.
- No ticket deletion.
- No GUI or web interface (out of scope for the sprint).

## Reviewed pull requests

- Engineer A's PR: `<link>`
- Engineer B's PR: `<link>`
