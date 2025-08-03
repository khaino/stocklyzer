"""Custom exceptions for the stocklyzer service."""


class StocklyzerError(Exception):
    """Base exception for stocklyzer."""
    pass


class ValidationError(StocklyzerError):
    """Raised when input validation fails."""
    pass


class StockDataError(StocklyzerError):
    """Raised when stock data cannot be retrieved."""
    pass


class ServiceUnavailableError(StocklyzerError):
    """Raised when service is not available."""
    pass