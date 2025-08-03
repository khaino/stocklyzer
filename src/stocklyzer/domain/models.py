"""Pure domain models with no UI concerns."""

from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum


@dataclass
class GrowthMetrics:
    """Stock growth performance over different periods."""
    
    one_year: Optional[Decimal] = None
    two_years: Optional[Decimal] = None
    three_years: Optional[Decimal] = None
    five_years: Optional[Decimal] = None
    ten_years: Optional[Decimal] = None
    
    def __post_init__(self):
        """Validate and quantize growth percentages."""
        for field_name in ["one_year", "two_years", "three_years", "five_years", "ten_years"]:
            value = getattr(self, field_name)
            if value is not None:
                setattr(self, field_name, value.quantize(Decimal('0.01')))
    
    def get_growth(self, period: str) -> Optional[Decimal]:
        """Get growth for a specific period."""
        period_map = {
            "1y": self.one_year,
            "2y": self.two_years,
            "3y": self.three_years,
            "5y": self.five_years,
            "10y": self.ten_years
        }
        return period_map.get(period.lower())


@dataclass
class FinancialPeriod:
    """Single period financial data."""
    date: datetime
    total_revenue: Optional[Decimal] = None
    net_income: Optional[Decimal] = None
    total_assets: Optional[Decimal] = None
    total_liabilities: Optional[Decimal] = None
    total_equity: Optional[Decimal] = None
    shares_outstanding: Optional[int] = None
    
    def __post_init__(self):
        """Validate and quantize financial values."""
        # Convert to millions and quantize to 2 decimal places
        for field_name in ["total_revenue", "net_income", "total_assets", "total_liabilities", "total_equity"]:
            value = getattr(self, field_name)
            if value is not None:
                # Convert to millions if the value is large (assuming input is in actual dollars)
                if value > 1_000_000:
                    value = value / 1_000_000
                setattr(self, field_name, value.quantize(Decimal('0.01')))


@dataclass
class FinancialHistory:
    """Historical financial data with growth calculations."""
    annual_periods: List[FinancialPeriod] = field(default_factory=list)
    quarterly_periods: List[FinancialPeriod] = field(default_factory=list)
    
    def get_revenue_growth(self, period_type: str = "annual") -> List[Optional[Decimal]]:
        """Calculate revenue growth rates."""
        periods = self.annual_periods if period_type == "annual" else self.quarterly_periods
        return self._calculate_growth_rates(periods, "total_revenue")
    
    def get_net_income_growth(self, period_type: str = "annual") -> List[Optional[Decimal]]:
        """Calculate net income growth rates."""
        periods = self.annual_periods if period_type == "annual" else self.quarterly_periods
        return self._calculate_growth_rates(periods, "net_income")
    
    def get_balance_sheet_growth(self) -> Dict[str, List[Optional[Decimal]]]:
        """Calculate balance sheet growth rates."""
        return {
            "assets": self._calculate_growth_rates(self.annual_periods, "total_assets"),
            "liabilities": self._calculate_growth_rates(self.annual_periods, "total_liabilities"),
            "equity": self._calculate_growth_rates(self.annual_periods, "total_equity")
        }
    
    def _calculate_growth_rates(self, periods: List[FinancialPeriod], metric: str) -> List[Optional[Decimal]]:
        """Calculate period-over-period growth rates."""
        if len(periods) < 2:
            return []
        
        growth_rates = []
        
        for i in range(len(periods) - 1):
            current = getattr(periods[i], metric)      # More recent (index 0 is most recent)
            previous = getattr(periods[i + 1], metric) # Older period
            
            if current is not None and previous is not None and previous != 0:
                growth = ((current - previous) / previous) * 100
                growth_rates.append(growth.quantize(Decimal('0.1')))
            else:
                growth_rates.append(None)
        
        return growth_rates


@dataclass
class PriceRange:
    """Price range information."""
    
    week_52_low: Decimal
    week_52_high: Decimal
    day_low: Decimal
    day_high: Decimal
    
    def __post_init__(self):
        """Validate and quantize prices."""
        if self.week_52_low >= self.week_52_high:
            raise ValueError("52-week low must be less than 52-week high")
        if self.day_low > self.day_high:
            raise ValueError("Day low must be less than or equal to day high")
        
        # Quantize to 2 decimal places
        self.week_52_low = self.week_52_low.quantize(Decimal('0.01'))
        self.week_52_high = self.week_52_high.quantize(Decimal('0.01'))
        self.day_low = self.day_low.quantize(Decimal('0.01'))
        self.day_high = self.day_high.quantize(Decimal('0.01'))
    
    def calculate_position_in_range(self, current_price: Decimal) -> Decimal:
        """Calculate position in 52-week range (0.0 to 1.0)."""
        if self.week_52_high <= self.week_52_low:
            return Decimal('0.5')
        
        position = (current_price - self.week_52_low) / (self.week_52_high - self.week_52_low)
        return max(Decimal('0'), min(Decimal('1'), position))
    
    @property
    def range_width(self) -> Decimal:
        """Calculate 52-week range width."""
        return self.week_52_high - self.week_52_low


@dataclass
class StockInfo:
    """Pure stock information domain model."""
    
    # Basic identification (required)
    symbol: str
    company_name: str
    
    # Price information (required)
    current_price: Decimal
    change: Decimal
    change_percent: Decimal
    
    # Trading data (required)
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    volume: int
    
    # Metadata (required)
    last_updated: datetime
    
    # Market metrics (optional)
    market_cap: Optional[int] = None
    pe_ratio: Optional[Decimal] = None
    eps: Optional[Decimal] = None
    book_value: Optional[Decimal] = None
    
    # Dividend information (optional)
    dividend_yield: Optional[Decimal] = None  # Annual dividend yield as percentage
    dividend_rate: Optional[Decimal] = None   # Annual dividend per share in dollars
    ex_dividend_date: Optional[datetime] = None  # Most recent ex-dividend date
    dividend_date: Optional[datetime] = None     # Most recent dividend payment date
    
    # Company information (optional)
    sector: Optional[str] = None
    quote_type: Optional[str] = None  # "ETF", "EQUITY", "MUTUALFUND", etc.
    category: Optional[str] = None    # Fund category for ETFs
    
    # Calculated metrics (optional)
    growth_metrics: Optional[GrowthMetrics] = None
    price_range: Optional[PriceRange] = None
    financial_history: Optional[FinancialHistory] = None
    data_quality_score: float = 1.0
    
    def __post_init__(self):
        """Validate data after initialization."""
        if self.current_price <= 0:
            raise ValueError(f"Invalid price: {self.current_price}")
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")
        
        # Ensure proper decimal precision
        self.current_price = self.current_price.quantize(Decimal('0.01'))
        self.change = self.change.quantize(Decimal('0.01'))
        self.change_percent = self.change_percent.quantize(Decimal('0.01'))
        
        # Quantize dividend fields if present
        if self.dividend_yield is not None:
            self.dividend_yield = self.dividend_yield.quantize(Decimal('0.01'))
        if self.dividend_rate is not None:
            self.dividend_rate = self.dividend_rate.quantize(Decimal('0.01'))
    
    @property
    def is_profitable(self) -> Optional[bool]:
        """Check if company is profitable based on EPS."""
        return self.eps > 0 if self.eps is not None else None
    
    @property
    def is_price_increasing(self) -> bool:
        """Check if price is increasing."""
        return self.change > 0
    
    @property
    def is_price_decreasing(self) -> bool:
        """Check if price is decreasing."""
        return self.change < 0
    
    @property
    def pays_dividend(self) -> bool:
        """Check if the stock pays dividends."""
        return (self.dividend_rate is not None and self.dividend_rate > 0) or \
               (self.dividend_yield is not None and self.dividend_yield > 0)
    
    @property
    def market_cap_category(self) -> str:
        """Categorize market cap size."""
        if not self.market_cap:
            return "unknown"
        
        if self.market_cap >= 200e9:
            return "mega_cap"
        elif self.market_cap >= 10e9:
            return "large_cap"
        elif self.market_cap >= 2e9:
            return "mid_cap"
        elif self.market_cap >= 300e6:
            return "small_cap"
        else:
            return "micro_cap"
    
    def get_display_classification(self) -> str:
        """Get appropriate classification for display."""
        if self.quote_type == 'ETF' and self.category:
            return self.category  # e.g., "Large Blend", "Small Growth"
        elif self.quote_type == 'MUTUALFUND':
            return "Mutual Fund"
        elif self.quote_type == 'CRYPTOCURRENCY':
            return "Cryptocurrency"
        elif self.quote_type == 'CURRENCY':
            return "Currency"
        elif self.sector:
            return self.sector  # For regular stocks
        else:
            return "Unknown"


class MarketCapSize(Enum):
    """Market capitalization categories."""
    NANO = "nano"
    MICRO = "micro"
    SMALL = "small"
    MID = "mid"
    LARGE = "large"
    MEGA = "mega"


class DataQuality(Enum):
    """Data quality indicators."""
    EXCELLENT = 1.0
    GOOD = 0.8
    FAIR = 0.6
    POOR = 0.4
    UNAVAILABLE = 0.0