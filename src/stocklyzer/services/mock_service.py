"""Mock service for testing."""

from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict

from .interfaces import StockService
from ..domain.models import StockInfo, GrowthMetrics, PriceRange, FinancialHistory, FinancialPeriod


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
            three_years=Decimal('25.48'),
            five_years=Decimal('91.11'),
            ten_years=Decimal('662.93')
        )
        
        apple_range = PriceRange(
            week_52_low=Decimal('164.08'),
            week_52_high=Decimal('237.49'),
            day_low=Decimal('201.50'),
            day_high=Decimal('205.44')
        )
        
        # Create sample financial history
        apple_financial_history = FinancialHistory()
        
        # Annual periods (most recent first)
        apple_financial_history.annual_periods = [
            FinancialPeriod(
                date=datetime(2024, 9, 30),
                total_revenue=Decimal('391035'),  # $391.035B
                net_income=Decimal('93736'),     # $93.736B
                total_assets=Decimal('364980'),
                total_liabilities=Decimal('308030'),
                total_equity=Decimal('56950'),
                shares_outstanding=15204000000
            ),
            FinancialPeriod(
                date=datetime(2023, 9, 30),
                total_revenue=Decimal('383285'),  # $383.285B
                net_income=Decimal('96995'),     # $96.995B
                total_assets=Decimal('352755'),
                total_liabilities=Decimal('290437'),
                total_equity=Decimal('62318'),
                shares_outstanding=15550000000
            ),
            FinancialPeriod(
                date=datetime(2022, 9, 30),
                total_revenue=Decimal('394328'),  # $394.328B
                net_income=Decimal('99803'),     # $99.803B
                total_assets=Decimal('352583'),
                total_liabilities=Decimal('302083'),
                total_equity=Decimal('50500'),
                shares_outstanding=15943000000
            ),
            FinancialPeriod(
                date=datetime(2021, 9, 30),
                total_revenue=Decimal('365817'),  # $365.817B
                net_income=Decimal('94680'),     # $94.680B
                total_assets=Decimal('351002'),
                total_liabilities=Decimal('287912'),
                total_equity=Decimal('63090'),
                shares_outstanding=16426000000
            )
        ]
        
        # Quarterly periods (most recent first)
        apple_financial_history.quarterly_periods = [
            FinancialPeriod(
                date=datetime(2024, 9, 30),
                total_revenue=Decimal('94930'),   # Q3 2024
                net_income=Decimal('14736'),
                total_assets=Decimal('364980'),
                total_liabilities=Decimal('308028'),
                total_equity=Decimal('56952'),
                shares_outstanding=15117000000
            ),
            FinancialPeriod(
                date=datetime(2024, 6, 30),
                total_revenue=Decimal('85777'),   # Q2 2024
                net_income=Decimal('21448'),
                total_assets=Decimal('357000'),
                total_liabilities=Decimal('301000'),
                total_equity=Decimal('56000'),
                shares_outstanding=15204000000
            ),
            FinancialPeriod(
                date=datetime(2024, 3, 31),
                total_revenue=Decimal('90753'),   # Q1 2024
                net_income=Decimal('23636'),
                total_assets=Decimal('355000'),
                total_liabilities=Decimal('298000'),
                total_equity=Decimal('57000'),
                shares_outstanding=15350000000
            ),
            FinancialPeriod(
                date=datetime(2023, 12, 31),
                total_revenue=Decimal('119575'),  # Q4 2023
                net_income=Decimal('33916'),
                total_assets=Decimal('353000'),
                total_liabilities=Decimal('291000'),
                total_equity=Decimal('62000'),
                shares_outstanding=15550000000
            )
        ]
        
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
            dividend_yield=Decimal('0.44'),  # 0.44% dividend yield
            dividend_rate=Decimal('0.96'),   # $0.96 annual dividend per share
            ex_dividend_date=datetime(2024, 11, 8),  # Example ex-dividend date
            dividend_date=datetime(2024, 11, 14),    # Example dividend payment date
            sector="Technology",
            quote_type="EQUITY",
            category=None,
            growth_metrics=apple_growth,
            price_range=apple_range,
            financial_history=apple_financial_history,
            last_updated=datetime.now(),
            data_quality_score=1.0
        )
        
        return {
            "AAPL": apple_stock
        }