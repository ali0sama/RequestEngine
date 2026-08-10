class InvalidTransitionError(Exception):
    """Raised when a (current_state, action) pair has no valid transition."""


class UnauthorizedActionError(Exception):
    """Raised when the actor's role or ownership doesn't permit this action."""
