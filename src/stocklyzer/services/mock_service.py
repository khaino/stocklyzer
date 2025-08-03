"""Mock service for testing."""

from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict

from .interfaces import StockService
from ..domain.models import StockInfo, GrowthMetrics, PriceRange


class MockStockService(StockService):
    """Mock stock service for testing."""
    
    def __init__(self, symbol: str, mock_data: Optional[Dict[str, StockInfo]] = None):
        """Initialize with symbol and mock data."""
        self._symbol = symbol.upper()
        self._mock_data = mock_data or self._create_default_mock_data()
    
    async def get_stock_info(self) -> Optional[StockInfo]:
        """Get mock stock information for the initialized symbol."""
        return self._mock_data.get(self._symbol)
    
    def validate_symbol(self, symbol: str) -> bool:
        """Simple mock validation."""
        return isinstance(symbol, str) and 1 <= len(symbol) <= 5 and symbol.isalpha()
    
    def is_available(self) -> bool:
        """Mock service is always available."""
        return True
    
    @property
    def service_name(self) -> str:
        """Get service name."""
        return "Mock Service"
    
    @property
    def symbol(self) -> str:
        """Get the symbol this service is initialized for."""
        return self._symbol
    
    def _create_default_mock_data(self) -> Dict[str, StockInfo]:
        """Create default mock data for testing."""
        apple_growth = GrowthMetrics(
            one_year=Decimal('-7.52'),
            two_years=Decimal('6.14'),
            five_years=Decimal('91.11'),
            ten_years=Decimal('662.93')
        )
        
        apple_range = PriceRange(
            week_52_low=Decimal('164.08'),
            week_52_high=Decimal('237.49'),
            day_low=Decimal('201.50'),
            day_high=Decimal('205.44')
        )
        
        apple_stock = StockInfo(
            symbol="AAPL",
            company_name="Apple Inc.",
            current_price=Decimal('202.38'),
            change=Decimal('-5.18'),
            change_percent=Decimal('-2.50'),
            open_price=Decimal('205.00'),
            high_price=Decimal('205.44'),
            low_price=Decimal('201.50'),
            volume=45234567,
            market_cap=3000000000000,
            pe_ratio=Decimal('30.66'),
            eps=Decimal('6.60'),
            book_value=Decimal('4.43'),
            sector="Technology",
            growth_metrics=apple_growth,
            price_range=apple_range,
            last_updated=datetime.now(),
            data_quality_score=1.0
        )
        
        return {
            "AAPL": apple_stock
        }