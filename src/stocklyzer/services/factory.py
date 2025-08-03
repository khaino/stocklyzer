"""Service factory for dependency injection."""

from .interfaces import StockService
from .stock_service import YFinanceStockService
from .mock_service import MockStockService


class ServiceFactory:
    """Factory for creating stock services."""
    
    @staticmethod
    def create_stock_service(symbol: str, service_type: str = "yfinance") -> StockService:
        """Create stock service for a specific symbol."""
        if service_type.lower() == "yfinance":
            return YFinanceStockService(symbol)
        elif service_type.lower() == "mock":
            return MockStockService(symbol)
        else:
            raise ValueError(f"Unknown service type: {service_type}")