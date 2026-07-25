class InvalidTransitionError(Exception):
    """Raised when a (current_state, action) pair has no valid transition."""
    pass


class UnauthorizedActionError(Exception):
    """Raised when the actor's role or ownership doesn't permit this action."""
    pass