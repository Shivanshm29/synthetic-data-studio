class DuplicateStrategyError(Exception):
    """Raised when multiple strategies support the same field."""
    pass


class StrategyNotFoundError(Exception):
    """Raised when no strategy exists for a field."""
    pass