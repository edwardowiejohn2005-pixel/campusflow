"""Custom exceptions shared by all CampusFlow modules.

Design decision: business logic signals problems by raising these exceptions;
the CLI catches them and prints the message. Tests can assert on them without
any interactive input.
"""


class CampusFlowError(Exception):
    """Base class for all CampusFlow errors."""


class ValidationError(CampusFlowError, ValueError):
    """Raised when user input for a ticket is invalid."""


class TicketNotFoundError(CampusFlowError, KeyError):
    """Raised when a ticket ID does not exist."""

    def __str__(self):
        # KeyError wraps its message in quotes; keep it readable.
        return str(self.args[0]) if self.args else "Ticket not found."


class InvalidTransitionError(CampusFlowError):
    """Raised when a status change is not allowed."""


class StorageError(CampusFlowError):
    """Raised when the JSON file cannot be read or written safely."""
