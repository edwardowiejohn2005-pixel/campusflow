# Design Decisions

Agreed contracts for CampusFlow. Review these together before branching; edit anything your team decides differently.

## Ownership

| Area | Owner | Files |
|---|---|---|
| Ticket creation, input validation, priority engine | Engineer A | `campusflow/tickets.py`, `tests/test_tickets.py` |
| Assignment, lifecycle, work queue, reports | Engineer B | `campusflow/workflow.py`, `campusflow/reports.py`, `tests/test_workflow.py` |
| JSON persistence, CLI, docs | Shared | `campusflow/storage.py`, `campusflow/cli.py`, `tests/test_storage.py`, `docs/` |

## Contracts

**Where tickets live:** one in-memory `list` of `dict`s. The list is created by `storage.load_tickets()` and passed as the first argument to every function that reads or changes tickets. There is no global state, so tests can build their own list.

**How invalid input is signalled:** functions raise exceptions from `campusflow/errors.py`; they never print or call `input()`.

| Exception | Raised when |
|---|---|
| `ValidationError` | Bad title, category, urgency, `affected_users`, or staff name |
| `TicketNotFoundError` | Unknown ticket ID |
| `InvalidTransitionError` | Illegal status change, or editing a resolved ticket |
| `StorageError` | Unreadable/malformed JSON, or a failed save |

The CLI catches `CampusFlowError` and prints `Error: <message>`, then returns to the menu.

**Return values:** `create_ticket`, `assign_ticket`, `change_status`, and `reopen_ticket` return the changed ticket dict. `work_queue` returns a new sorted list. `build_report` returns a dict with `total`, `by_status`, and `by_priority`.

**No corruption on failure:** every function validates before changing anything, so a rejected call leaves the list unchanged. Tests assert this.

**Who owns JSON:** only `storage.py` touches the file (`load_tickets(path)`, `save_tickets(tickets, path)`). The CLI saves after each successful change. Saves write to a temp file and then replace the real one, so a crash cannot leave a half-written file.

**How logic is tested without keyboard input:** business logic takes plain arguments. The CLI's `run()` accepts `input_fn` and `output_fn`, so tests feed scripted answers and capture output.

## Decisions on ambiguous points

| Question | Decision | Why |
|---|---|---|
| Does the queue include `in_progress` tickets? | No, only `open` | The spec says "open, unresolved tickets" and lists `open` as the state; in-progress work is already being handled. Documented as a limitation. |
| Can a ticket be reassigned? | Yes, unless resolved | Staff change; blocking reassignment would be unhelpful. |
| Can status move backwards (in_progress → open)? | No | Spec defines the forward flow plus an explicit reopen from resolved only. |
| ID generation | highest existing number + 1 | Stays unique after reload and never reuses a gap. |
| Numeric ordering of IDs | parse the digits (`T010` > `T002`) | String sorting breaks past `T999` and is fragile. |
| `affected_users` input | strict: digits only | Rejects `2.5`, `-3`, `abc`, booleans, and empty text. |

## Branch plan

- `feat/1-ticket-creation` (Engineer A)
- `feat/2-status-workflow` (Engineer B)
- Integration fixes via a new reviewed PR, e.g. `fix/<n>-<description>`.
