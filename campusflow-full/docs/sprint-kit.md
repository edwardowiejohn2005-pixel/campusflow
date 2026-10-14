# Sprint Kit

Copy-paste material for the parts of the sprint that happen on GitHub. The code and tests are already in this folder; the **process evidence** (real commits, real reviews, real AI experiments) has to come from the two of you.

## 1. Repository setup (Phase 1)

```bash
# one person, inside this folder
git init -b main
git add .
git commit -m "chore: initial CampusFlow project"
gh repo create campusflow-<team-id> --private --source=. --push
# invite your partner: repo -> Settings -> Collaborators
```

Both Fellows: `git config user.name "..."` and `git config user.email "..."` with your own identity, then clone.

## 2. GitHub Issues (Phase 2)

| # | Title | Acceptance criteria | Owner |
|---|---|---|---|
| 1 | Ticket creation, validation and priority engine | Valid ticket is created with auto ID · `affected_users=0`, negative, decimal, text rejected · blank title rejected · invalid category/urgency rejected · priority rules give high+12 → critical, high+2 → high, low+4 → medium, low+1 → low · rejected input leaves list unchanged | A |
| 2 | Assignment, status workflow, queue and reports | Unknown ID rejected · blank staff name rejected · unassigned ticket cannot enter `in_progress` · open → in_progress → resolved works · resolved ticket locked until reopened · queue sorted by priority then numeric ID · empty report shows zeros | B |
| 3 | JSON persistence and CLI | Save/reload keeps tickets · missing file = fresh start · corrupt file gives clear error and is not overwritten · IDs unique after reload · menu runs until Exit | A + B |
| 4 | Documentation | README, design decisions, AI log complete | A + B |

## 3. How to split the existing code into two real PRs

The code is already written, so for the guide's "each Fellow authors a PR" rule to be honest, each of you should **own, understand, and be able to change** your half. Suggested approach:

1. Commit only the shared skeleton to `main` first: `.gitignore`, `README.md`, `campusflow/__init__.py`, `campusflow/errors.py`, `tests/__init__.py`.
2. **Engineer A** branches `feat/1-ticket-creation` and adds `campusflow/tickets.py` + `tests/test_tickets.py`, in several small commits.
3. **Engineer B** branches `feat/2-status-workflow` and adds `campusflow/workflow.py`, `campusflow/reports.py` + `tests/test_workflow.py`.
4. After both are merged, add `storage.py`, `cli.py`, `main.py`, `tests/test_storage.py` via a third reviewed PR (`feat/3-persistence-cli`), split between you.

Before you open a PR, read your files line by line. If you cannot explain a line, change it, simplify it, or ask for an explanation. You will be questioned in the defence. Extend your own tests too (e.g. add a case you think is missing).

Note: `workflow.py` imports from `tickets.py`, so Engineer B's branch needs A's merged first (or B temporarily branches from A's branch). Plan for the "update your branch from main" step in the guide (section 4.6).

## 4. Branch, commit, PR commands

```bash
git switch main && git pull origin main
git switch -c feat/1-ticket-creation
git status && git diff
git add campusflow/tickets.py tests/test_tickets.py
git commit -m "feat: add ticket validation and priority engine"
git push -u origin feat/1-ticket-creation
```

Reviewer checks out the PR branch without editing it:

```bash
git fetch origin
git switch --detach origin/feat/1-ticket-creation
python -m unittest discover -s tests -v
git switch main
```

## 5. PR description (fill in honestly)

```
PR TITLE: feat: ticket creation, validation and priority engine
Related Issue: Closes #1

WHAT CHANGED?
- Added campusflow/tickets.py and tests/test_tickets.py

HOW DOES IT WORK?
- <your explanation: validation first, then build + append; priority via ordered rules>

HOW DID I TEST IT?
- Command: python -m unittest discover -s tests -v
- Actual result: <paste your real output summary, e.g. "Ran N tests ... OK">
- Edge cases: <what you verified>

WHAT DID I LEARN WITH AI?
- Concept: <topic>
- My verification: <experiment or test>
- Changed/rejected advice: <if applicable>

REVIEWER NOTES
- What I want my partner to check: <specific risk, e.g. is "10" parsed as 10 and "1e1" rejected?>

KNOWN LIMITATIONS
- <honest gaps>
```

## 6. Review prompts (leave at least two substantive comments per PR)

Things worth actually checking:

- Does `calculate_priority("high", 10)` return `critical` and `("medium", 10)` return `high`? Run it.
- Does a rejected `create_ticket` leave the list unchanged? Is that tested?
- Is `"2.5"`, `"-1"`, `True` rejected for `affected_users`?
- Does the queue sort by numeric ID (`T010` after `T002`)? Is there a test?
- Can a resolved ticket be assigned? Should it be?
- What happens with a half-written or corrupted JSON file?
- Are tests asserting results or only checking that no exception happened?

Use **Request changes** if you find a real problem; the author fixes on the same branch and you re-review before approving. Never approve your own PR.

## 7. AI learning topic ideas (Phase 3)

Pick topics you genuinely don't yet understand. For each: write what you think, ask for a small *unrelated* example, predict the output, run it, verify, then explain in your own words.

- `json.dump` / `json.load` and what `JSONDecodeError` is
- `try` / `except` and raising custom exceptions
- `unittest`: `assertEqual`, `assertRaises`, `setUp`, `subTest`
- Why `sorted(..., key=lambda ...)` with a tuple key works
- Git: `switch`, `merge`, resolving conflicts, detached checkout
- Atomic file writes (`tempfile`, `os.replace`): why not just `open(path, "w")`?

For the "critical evaluation" entry: ask AI to review a small piece of your code, then *run the claim yourself*. If it says a function has a bug, write the failing test. If the test passes, document that you rejected the suggestion and why.

## 8. Demo script (20 minutes)

1. `python -m unittest discover -s tests -v` (show all green)
2. `rm -f data/tickets.json && python main.py`
3. Create: Wi-Fi/Network/high/15 → critical; Laptop/Hardware/low/1 → low; Printer/hardware/medium/4 → medium
4. Create with `0` affected users → error shown
5. Assign T001, move to in_progress; try T002 → in_progress unassigned → error; try T001 in_progress → open → error
6. Resolve T001; try to assign it → error; reopen it
7. Work queue (critical first) and Reports
8. Exit, restart, list (data persisted), create a new ticket and show the ID continues
9. Show both PRs and reviews on GitHub
10. Each Fellow explains one decision, one test, and one AI suggestion they verified/changed/rejected

## 9. Final individual reflection (answer separately)

1. Which feature did you personally implement, and how do you know it works?
2. What did AI teach you that you did not understand at the start?
3. Give one example where you verified, changed, or rejected an AI suggestion.
4. What did you learn from reviewing your partner's PR?
5. What would you improve next if the team had another hour?
