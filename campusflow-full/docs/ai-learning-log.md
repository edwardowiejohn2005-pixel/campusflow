# CampusFlow Next — AI Learning Log

**Project:** CampusFlow Next  
**Role:** Engineer A — Ticket Safety and Storage Engineer  
**Branch:** `feat/21-validation-and-notes`

## Learning Cycle 1: Ticket Schema Changes and Regression Testing

### 1. What I Did Not Understand

Initially, I did not fully understand why an existing automated test would fail after adding a new required field to a ticket dictionary.

I added the `notes` field to my `create_ticket()` function, but one existing test started failing.

### 2. How I Used AI

I shared my unittest failure output with ChatGPT for guidance.

The error occurred in:

`test_create_valid_ticket_has_all_fields`

The test expected the original ticket dictionary without the new `notes` field, but my updated function returned a dictionary containing `"notes": []`.

### 3. What AI Explained

AI explained that the failure happened because the test compared the entire ticket dictionary against an older expected structure.

It suggested updating the expected dictionary in the test to include the new field instead of removing the required functionality.

### 4. What I Changed in My Code

I retained the following field inside `create_ticket()`:

```python
"notes": [],
```

I also updated the expected dictionary inside `tests/test_tickets.py` to include the same field.

### 5. Independent Verification

I ran:

```bash
python3 -m unittest discover -s tests -v
```

Before the test correction:

- Total tests: 38
- Passed: 37
- Failed: 1

After updating the expected dictionary:

- Total tests: 38
- Passed: 38
- Failed: 0
- Execution time: 0.015 seconds

This confirmed that the updated ticket structure passed the existing and newly added tests.

### 6. Small Independent Experiment

To explore this concept further, I will test a separate dictionary example unrelated to CampusFlow.

```python
book = {
    "title": "Python Basics",
    "author": "John"
}

expected = {
    "title": "Python Basics",
    "author": "John",
    "chapters": []
}

print(book == expected)
```

Expected result: `False`, because the dictionaries contain different keys.

**Actual result:** To be recorded after running the experiment.

### 7. Final Engineering Decision

I decided to preserve the required `notes` field and update the outdated test expectation.

I learned that when a software requirement changes, tests may also need updating. However, a failing test must be investigated before assuming that the test itself is wrong.

### 8. What I Can Explain Without AI

I can explain why adding a new dictionary key changes the result of an equality comparison.

I can also explain how automated tests help identify unintended changes when new features are introduced.

---

## Learning Cycle 2: Safe JSON Validation and Data Integrity

**Status:** Not yet completed.

This section will document my next learning activity involving:

- Validating JSON records before loading.
- Detecting duplicate ticket IDs.
- Preventing data loss when loading invalid files.
- Writing tests for unsuccessful loading operations.
- Independently verifying AI suggestions.

I will complete this section after implementing and testing the JSON validation improvements.