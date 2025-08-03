"""Growth calculation utilities."""

import yfinance as yf
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class GrowthCalculator:
    """Handles growth calculations with date validation."""
    
    async def calculate_growth(self, ticker: yf.Ticker, period: str) -> Optional[Decimal]:
        """Calculate growth for a specific period using existing ticker."""
        try:
            hist_start = ticker.history(period=period)
            hist_end = ticker.history(period="1d")
            
            if hist_start.empty or hist_end.empty:
                return None
            
            # Check if we have sufficient data for the requested period
            actual_start_date = hist_start.index[0]
            current_date = datetime.now().replace(tzinfo=actual_start_date.tz)
            
            # Calculate required lookback period
            required_years = self._period_to_years(period)
            required_date = current_date - timedelta(days=required_years * 365 * 0.8)
            
            if actual_start_date > required_date:
                # Not enough historical data
                return None
            
            start_price = float(hist_start.iloc[0]['Close'])
            end_price = float(hist_end.iloc[-1]['Close'])
            
            if start_price <= 0:
                return None
            
            growth = ((end_price - start_price) / start_price) * 100
            return Decimal(str(growth))
            
        except Exception as e:
            logger.warning(f"Failed to calculate {period} growth: {e}")
            return None
    
    def _period_to_years(self, period: str) -> int:
        """Convert period string to years."""
        period_map = {
            "1y": 1,
            "2y": 2,
            "5y": 5,
            "10y": 10
        }
        return period_map.get(period.lower(), 1)