# FSM_exceptions.py

class BanzukeParsingError(Exception):
    """Base exception for all FSM-related parsing errors."""
    pass

class ReconciliationError(BanzukeParsingError):
    """Raised when the body data mismatches the margin data."""
    pass

class UnclassifiableRowError(BanzukeParsingError):
    """Raised when a raw banzuke row cannot be classified into a token."""
    pass

class RankOrderValidationError(BanzukeParsingError):
    """Raised when the banzuke rank order is not monotonically increasing."""
    pass
