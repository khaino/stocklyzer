"""Service layer interfaces."""

from abc import ABC, abstractmethod
from typing import Optional
from ..domain.models import StockInfo


class StockService(ABC):
    """Interface for stock analysis services."""
    
    @abstractmethod
    async def get_stock_info(self) -> Optional[StockInfo]:
        """Get comprehensive stock information for the initialized symbol."""
        pass
    
    @abstractmethod
    def validate_symbol(self, symbol: str) -> bool:
        """Validate stock symbol format."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if service is available."""
        pass
    
    @property
    @abstractmethod
    def service_name(self) -> str:
        """Get service name."""
        pass
    
    @property
    @abstractmethod
    def symbol(self) -> str:
        """Get the symbol this service is initialized for."""
        pass