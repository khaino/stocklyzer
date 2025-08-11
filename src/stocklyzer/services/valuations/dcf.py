"""Discounted Cash Flow (DCF) valuation models and calculations."""

from decimal import Decimal
from typing import Optional, Tuple
import yfinance as yf
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DiscountedCashFlow:
    """Discounted Cash Flow valuation model."""
    
    def __init__(self, ticker, perpetual_growth_rate=0.025, required_return=0.1):
        """Initialize DCF model."""
        self.ticker = ticker
        self.perpetual_growth_rate = Decimal(str(perpetual_growth_rate))
        self.required_return = Decimal(str(required_return))
    
    def calculate_weighted_average_cost_of_capital(self) -> Optional[Decimal]:
        """Calculate WACC."""
        try:
            # Get data
            info = self.ticker.info
            
            # Basic components
            market_cap = Decimal(str(info['marketCap']))
            beta = Decimal(str(info.get('beta', 1.0)))
            
            # Treasury rate
            treasury_10y = Decimal(str(yf.Ticker("^TNX").history(period="1d").iloc[-1]['Close'] / 100))
            
            # Cost of Equity = Treasury + Beta * (Required Return - Treasury)
            cost_of_equity = treasury_10y + beta * (self.required_return - treasury_10y)
            cost_of_equity = Decimal(str(cost_of_equity))
            
            # Cost of Debt - try to calculate from Interest Expense, fallback to previous years
            cost_debt_result = self._get_cost_of_debt_and_total_debt()
            cost_of_debt, total_debt = cost_debt_result

            # wacc
            total_value = total_debt + market_cap
            wacc = cost_of_debt * (total_debt / total_value) + cost_of_equity * (market_cap / total_value)
            logger.info(f"Ticker: {getattr(self.ticker, 'ticker', 'unknown')} | WACC: {wacc:.6f}")
            return wacc
            
        except Exception as e:
            logger.error(f"WACC calculation failed for {getattr(self.ticker, 'ticker', 'unknown')}: {str(e)}")
            return None
    
    def _get_cost_of_debt_and_total_debt(self) -> Optional[Tuple[Decimal, Decimal]]:
        """Get cost of debt and total debt from the same year, trying current year first, then previous years."""
        
        # Try each year's data
        for col in self.ticker.financials.columns:
            financial_sheet_year = self.ticker.financials[col]
            balance_sheet_year = self.ticker.balance_sheet[col]
            
            # Look for Interest Expense first
            if 'Interest Expense' not in financial_sheet_year.index or pd.isna(financial_sheet_year['Interest Expense']):
                continue  # Skip this year if no Interest Expense
                
            interest_expense = abs(float(financial_sheet_year['Interest Expense']))
            # Get debt data from the same year only (no fallback for individual components)
            long_term_debt = balance_sheet_year.get('Long Term Debt')
            current_debt = balance_sheet_year.get('Current Debt')

            # Convert to float, handling NaN values - skip only if BOTH are missing
            if pd.isna(long_term_debt) and pd.isna(current_debt):
                continue  # Skip if no debt data available for this year
            
            if pd.isna(current_debt):
                total_debt_year =  Decimal(balance_sheet_year.get('Total Debt'))
            else:
                long_term_debt = float(long_term_debt)
                current_debt = float(current_debt)
                total_debt_year = Decimal(str(long_term_debt + current_debt))
            
            # Calculate cost of debt: Interest Expense / Total Debt (same year)
            cost_of_debt = Decimal(str(interest_expense)) / Decimal(str(total_debt_year))

            logger.info(f"Using cost of debt from {col}: {cost_of_debt:.4f}, total debt: ${total_debt_year}")
            return (cost_of_debt, total_debt_year)
        
        # No data available
        logger.warning("Could not calculate cost of debt from financial data")
        return None


if __name__ == "__main__":
    ticker = yf.Ticker("PYPL")
    dcf = DiscountedCashFlow(ticker)
    wacc = dcf.calculate_weighted_average_cost_of_capital()
    print(f"WACC: {wacc}")
