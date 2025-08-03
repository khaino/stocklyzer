"""YFinance-based stock service implementation."""

import yfinance as yf
import logging
from decimal import Decimal
from datetime import datetime
from typing import Optional

from .interfaces import StockService
from ..domain.models import StockInfo, GrowthMetrics, PriceRange
from ..utils.calculations import GrowthCalculator
from ..utils.validators import SymbolValidator
from ..utils.exceptions import StockDataError, ValidationError

logger = logging.getLogger(__name__)


class YFinanceStockService(StockService):
    """Stock service implementation using Yahoo Finance."""
    
    def __init__(self, symbol: str):
        """Initialize service for a specific symbol."""
        if not symbol:
            raise ValueError("Symbol cannot be empty")
        
        self._symbol = symbol.upper()
        self._validator = SymbolValidator()
        self._calculator = GrowthCalculator()
        
        # Validate symbol format
        if not self._validator.is_valid_symbol(self._symbol):
            raise ValidationError(f"Invalid symbol format: {self._symbol}")
        
        # Initialize ticker for this symbol
        self._ticker = yf.Ticker(self._symbol)
    
    async def get_stock_info(self) -> Optional[StockInfo]:
        """Get comprehensive stock information for the initialized symbol."""
        try:
            # 1. Fetch raw data
            raw_data = await self._fetch_raw_data()
            if not raw_data:
                logger.warning(f"No raw data available for {self._symbol}")
                return None
            
            # 2. Process raw data into domain model
            stock_info = await self._process_stock_data(raw_data)
            
            if stock_info:
                logger.info(f"Successfully fetched data for {self._symbol}")
                return stock_info
            else:
                logger.warning(f"Failed to process data for {self._symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to fetch data for {self._symbol}: {e}")
            raise StockDataError(f"Unable to fetch data for {self._symbol}") from e
    
    async def _fetch_raw_data(self) -> Optional[dict]:
        """Fetch raw data from yfinance."""
        try:
            info = self._ticker.info
            hist = self._ticker.history(period="2d")
            
            if not info or hist.empty:
                return None
            
            # Validate essential data exists
            if 'symbol' not in info and 'shortName' not in info:
                return None
            
            return {
                'info': info,
                'hist': hist
            }
            
        except Exception as e:
            logger.error(f"Error fetching raw data for {self._symbol}: {e}")
            return None
    
    async def _process_stock_data(self, raw_data: dict) -> Optional[StockInfo]:
        """Process raw data into domain model."""
        try:
            info = raw_data['info']
            hist = raw_data['hist']
            
            # Calculate current price and change
            current_price = float(hist.iloc[-1]['Close'])
            previous_close = float(hist.iloc[-2]['Close']) if len(hist) > 1 else current_price
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100 if previous_close > 0 else 0
            
            # Apply business logic for financial metrics
            eps = info.get('trailingEps')
            pe_ratio = self._calculate_pe_ratio(info.get('trailingPE'), eps)
            
            # Calculate growth metrics
            growth_metrics = await self._calculate_growth_metrics()
            
            # Calculate price range
            price_range = await self._calculate_price_range(hist)
            
            # Build domain model
            stock_info = StockInfo(
                symbol=self._symbol,
                company_name=info.get('longName', info.get('shortName', f"{self._symbol} Corporation")),
                current_price=Decimal(str(current_price)),
                change=Decimal(str(change)),
                change_percent=Decimal(str(change_percent)),
                open_price=Decimal(str(float(hist.iloc[-1]['Open']))),
                high_price=Decimal(str(float(hist.iloc[-1]['High']))),
                low_price=Decimal(str(float(hist.iloc[-1]['Low']))),
                volume=int(hist.iloc[-1]['Volume']),
                market_cap=info.get('marketCap'),
                pe_ratio=pe_ratio,
                eps=Decimal(str(eps)) if eps is not None else None,
                book_value=Decimal(str(info.get('bookValue'))) if info.get('bookValue') else None,
                sector=info.get('sector'),
                growth_metrics=growth_metrics,
                price_range=price_range,
                last_updated=datetime.now(),
                data_quality_score=self._calculate_data_quality_score(info, growth_metrics)
            )
            
            return stock_info
            
        except Exception as e:
            logger.error(f"Error processing stock data for {self._symbol}: {e}")
            return None
    
    def _calculate_pe_ratio(self, raw_pe: Optional[float], eps: Optional[float]) -> Optional[Decimal]:
        """Apply business logic for P/E ratio calculation."""
        if not raw_pe or not eps:
            return None
        
        # No meaningful P/E for negative earnings
        if eps <= 0:
            return None
        
        # Validate reasonable P/E range (business rule)
        if raw_pe < 0 or raw_pe > 1000:
            return None
        
        return Decimal(str(raw_pe))
    
    async def _calculate_growth_metrics(self) -> Optional[GrowthMetrics]:
        """Calculate growth metrics using the initialized ticker."""
        try:
            growth_1y = await self._calculator.calculate_growth(self._ticker, "1y")
            growth_2y = await self._calculator.calculate_growth(self._ticker, "2y")
            growth_5y = await self._calculator.calculate_growth(self._ticker, "5y")
            growth_10y = await self._calculator.calculate_growth(self._ticker, "10y")
            
            return GrowthMetrics(
                one_year=growth_1y,
                two_years=growth_2y,
                five_years=growth_5y,
                ten_years=growth_10y
            )
        except Exception as e:
            logger.warning(f"Failed to calculate growth metrics for {self._symbol}: {e}")
            return None
    
    async def _calculate_price_range(self, recent_hist) -> Optional[PriceRange]:
        """Calculate price ranges using the initialized ticker."""
        try:
            # Get 52-week data using the same ticker
            hist_52w = self._ticker.history(period="1y")
            if hist_52w.empty:
                return None
            
            week_52_low = float(hist_52w['Low'].min())
            week_52_high = float(hist_52w['High'].max())
            day_low = float(recent_hist.iloc[-1]['Low'])
            day_high = float(recent_hist.iloc[-1]['High'])
            
            return PriceRange(
                week_52_low=Decimal(str(week_52_low)),
                week_52_high=Decimal(str(week_52_high)),
                day_low=Decimal(str(day_low)),
                day_high=Decimal(str(day_high))
            )
        except Exception as e:
            logger.warning(f"Failed to calculate price range: {e}")
            return None
    
    def _calculate_data_quality_score(self, info: dict, growth_metrics: Optional[GrowthMetrics]) -> float:
        """Calculate data quality score based on available information."""
        score = 0.0
        total_fields = 6
        
        # Check availability of key fields
        if info.get('marketCap'):
            score += 1
        if info.get('trailingPE'):
            score += 1
        if info.get('trailingEps'):
            score += 1
        if info.get('bookValue'):
            score += 1
        if info.get('sector'):
            score += 1
        if growth_metrics and growth_metrics.one_year is not None:
            score += 1
        
        return score / total_fields
    
    def validate_symbol(self, symbol: str) -> bool:
        """Validate stock symbol format."""
        return self._validator.is_valid_symbol(symbol)
    
    def is_available(self) -> bool:
        """Check if YFinance service is available."""
        try:
            # Simple availability check using our ticker
            info = self._ticker.info
            return bool(info and ('symbol' in info or 'shortName' in info))
        except Exception:
            return False
    
    @property
    def service_name(self) -> str:
        """Get service name."""
        return "Yahoo Finance"
    
    @property
    def symbol(self) -> str:
        """Get the symbol this service is initialized for."""
        return self._symbol