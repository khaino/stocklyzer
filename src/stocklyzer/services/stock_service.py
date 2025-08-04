"""YFinance-based stock service implementation."""

import yfinance as yf
import pandas as pd
import logging
from decimal import Decimal
from datetime import datetime
from typing import Optional

from .interfaces import StockService
from ..domain.models import StockInfo, GrowthMetrics, PriceRange, FinancialHistory, FinancialPeriod
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
            
            # Calculate financial history
            financial_history = await self._calculate_financial_history()
            
            # Extract dividend information - try different field names
            dividend_yield = info.get('dividendYield') or info.get('trailingAnnualDividendYield')
            dividend_rate = info.get('dividendRate') or info.get('trailingAnnualDividendRate')
            ex_dividend_date = info.get('exDividendDate')
            dividend_date = info.get('dividendDate')
            

            
            # Validate dividend yield is reasonable (Yahoo Finance returns as decimal, so 0.20 = 20%)
            # But sometimes it returns as percentage already, so check both ranges
            if dividend_yield is not None:
                if dividend_yield <= 0:
                    dividend_yield = None
                elif dividend_yield > 20:  # If > 20, likely already in percentage format, reject extreme values
                    logger.warning(f"Extreme dividend yield for {self._symbol}: {dividend_yield}%")
                    dividend_yield = None
                elif dividend_yield > 0.20:  # Between 0.20 and 20, assume it's percentage format
                    dividend_yield = dividend_yield / 100  # Convert to decimal format
            
            # Calculate dividend yield manually if we have dividend rate and current price
            if dividend_yield is None and dividend_rate is not None and current_price > 0:
                calculated_yield_percent = (dividend_rate / current_price) * 100
                if 0 < calculated_yield_percent <= 20:  # Reasonable range
                    dividend_yield = calculated_yield_percent / 100  # Store as decimal (0.0051 for 0.51%)
                    logger.info(f"Calculated dividend yield for {self._symbol}: {calculated_yield_percent:.2f}%")
            
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
                dividend_yield=Decimal(str(dividend_yield * 100)) if dividend_yield is not None and dividend_yield > 0 else None,  # Convert decimal to percentage for storage
                dividend_rate=Decimal(str(dividend_rate)) if dividend_rate is not None else None,
                ex_dividend_date=datetime.fromtimestamp(ex_dividend_date) if ex_dividend_date else None,
                dividend_date=datetime.fromtimestamp(dividend_date) if dividend_date else None,
                sector=info.get('sector'),
                quote_type=info.get('quoteType'),
                category=info.get('category'),
                growth_metrics=growth_metrics,
                price_range=price_range,
                financial_history=financial_history,
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
            growth_3y = await self._calculator.calculate_growth(self._ticker, "3y")
            growth_5y = await self._calculator.calculate_growth(self._ticker, "5y")
            growth_10y = await self._calculator.calculate_growth(self._ticker, "10y")
            
            return GrowthMetrics(
                one_year=growth_1y,
                two_years=growth_2y,
                three_years=growth_3y,
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
    
    async def _calculate_financial_history(self) -> Optional[FinancialHistory]:
        """Calculate financial history from Yahoo Finance data."""
        try:
            # Get financial statements
            annual_financials = self._ticker.financials
            quarterly_financials = self._ticker.quarterly_financials
            annual_balance_sheet = self._ticker.balance_sheet
            quarterly_balance_sheet = self._ticker.quarterly_balance_sheet
            annual_cash_flow = self._ticker.cashflow
            quarterly_cash_flow = self._ticker.quarterly_cashflow
            
            financial_history = FinancialHistory()
            
            # Process annual data
            if not annual_financials.empty and not annual_balance_sheet.empty:
                annual_periods = []
                
                # Get up to 4 years of data
                for date in annual_financials.columns[:4]:
                    try:
                        # Income statement data
                        total_revenue = annual_financials.loc['Total Revenue', date] if 'Total Revenue' in annual_financials.index else None
                        net_income = annual_financials.loc['Net Income', date] if 'Net Income' in annual_financials.index else None
                        
                        # Balance sheet data - using correct Yahoo Finance field names with fallbacks
                        total_assets = None
                        if 'Total Assets' in annual_balance_sheet.index:
                            total_assets = annual_balance_sheet.loc['Total Assets', date]
                        
                        total_liab = None
                        if 'Total Liabilities Net Minority Interest' in annual_balance_sheet.index:
                            total_liab = annual_balance_sheet.loc['Total Liabilities Net Minority Interest', date]
                        elif 'Total Liab' in annual_balance_sheet.index:
                            total_liab = annual_balance_sheet.loc['Total Liab', date]
                        
                        total_equity = None
                        if 'Stockholders Equity' in annual_balance_sheet.index:
                            total_equity = annual_balance_sheet.loc['Stockholders Equity', date]
                        elif 'Total Stockholder Equity' in annual_balance_sheet.index:
                            total_equity = annual_balance_sheet.loc['Total Stockholder Equity', date]
                        shares_outstanding = annual_balance_sheet.loc['Share Issued', date] if 'Share Issued' in annual_balance_sheet.index else None
                        
                        # Cash flow data (if available for this date)
                        operating_cash_flow = None
                        investing_cash_flow = None
                        financing_cash_flow = None
                        changes_in_cash = None
                        free_cash_flow = None
                        
                        if not annual_cash_flow.empty and date in annual_cash_flow.columns:
                            # Common yfinance cash flow field names with fallbacks
                            if 'Operating Cash Flow' in annual_cash_flow.index:
                                operating_cash_flow = annual_cash_flow.loc['Operating Cash Flow', date]
                            elif 'Total Cash From Operating Activities' in annual_cash_flow.index:
                                operating_cash_flow = annual_cash_flow.loc['Total Cash From Operating Activities', date]
                            
                            if 'Investing Cash Flow' in annual_cash_flow.index:
                                investing_cash_flow = annual_cash_flow.loc['Investing Cash Flow', date]
                            elif 'Total Cash From Investing Activities' in annual_cash_flow.index:
                                investing_cash_flow = annual_cash_flow.loc['Total Cash From Investing Activities', date]
                            
                            if 'Financing Cash Flow' in annual_cash_flow.index:
                                financing_cash_flow = annual_cash_flow.loc['Financing Cash Flow', date]
                            elif 'Total Cash From Financing Activities' in annual_cash_flow.index:
                                financing_cash_flow = annual_cash_flow.loc['Total Cash From Financing Activities', date]
                            
                            if 'Changes In Cash' in annual_cash_flow.index:
                                changes_in_cash = annual_cash_flow.loc['Changes In Cash', date]
                            elif 'Net Change In Cash' in annual_cash_flow.index:
                                changes_in_cash = annual_cash_flow.loc['Net Change In Cash', date]
                            
                            if 'Free Cash Flow' in annual_cash_flow.index:
                                free_cash_flow = annual_cash_flow.loc['Free Cash Flow', date]
                            elif operating_cash_flow is not None:
                                # Calculate free cash flow if not directly available
                                capex = None
                                if 'Capital Expenditures' in annual_cash_flow.index:
                                    capex = annual_cash_flow.loc['Capital Expenditures', date]
                                elif 'Capital Expenditure' in annual_cash_flow.index:
                                    capex = annual_cash_flow.loc['Capital Expenditure', date]
                                
                                if capex is not None:
                                    # CapEx is usually negative in yfinance, so we add it (subtract the absolute value)
                                    free_cash_flow = operating_cash_flow + capex
                        
                        period = FinancialPeriod(
                            date=date.to_pydatetime(),
                            total_revenue=Decimal(str(total_revenue)) if total_revenue is not None and not pd.isna(total_revenue) else None,
                            net_income=Decimal(str(net_income)) if net_income is not None and not pd.isna(net_income) else None,
                            total_assets=Decimal(str(total_assets)) if total_assets is not None and not pd.isna(total_assets) else None,
                            total_liabilities=Decimal(str(total_liab)) if total_liab is not None and not pd.isna(total_liab) else None,
                            total_equity=Decimal(str(total_equity)) if total_equity is not None and not pd.isna(total_equity) else None,
                            shares_outstanding=int(shares_outstanding) if shares_outstanding is not None and not pd.isna(shares_outstanding) else None,
                            operating_cash_flow=Decimal(str(operating_cash_flow)) if operating_cash_flow is not None and not pd.isna(operating_cash_flow) else None,
                            investing_cash_flow=Decimal(str(investing_cash_flow)) if investing_cash_flow is not None and not pd.isna(investing_cash_flow) else None,
                            financing_cash_flow=Decimal(str(financing_cash_flow)) if financing_cash_flow is not None and not pd.isna(financing_cash_flow) else None,
                            changes_in_cash=Decimal(str(changes_in_cash)) if changes_in_cash is not None and not pd.isna(changes_in_cash) else None,
                            free_cash_flow=Decimal(str(free_cash_flow)) if free_cash_flow is not None and not pd.isna(free_cash_flow) else None
                        )
                        annual_periods.append(period)
                        
                    except (KeyError, ValueError, TypeError) as e:
                        logger.debug(f"Error processing annual data for {date}: {e}")
                        continue
                
                financial_history.annual_periods = annual_periods
            
            # Process quarterly data
            if not quarterly_financials.empty:
                quarterly_periods = []
                
                # Get up to 4 quarters of data
                for date in quarterly_financials.columns[:4]:
                    try:
                        # Income statement data
                        total_revenue = quarterly_financials.loc['Total Revenue', date] if 'Total Revenue' in quarterly_financials.index else None
                        net_income = quarterly_financials.loc['Net Income', date] if 'Net Income' in quarterly_financials.index else None
                        
                        # Balance sheet data (if available for this quarter)
                        total_assets = None
                        total_liab = None
                        total_equity = None
                        shares_outstanding = None
                        
                        if not quarterly_balance_sheet.empty and date in quarterly_balance_sheet.columns:
                            if 'Total Assets' in quarterly_balance_sheet.index:
                                total_assets = quarterly_balance_sheet.loc['Total Assets', date]
                            
                            if 'Total Liabilities Net Minority Interest' in quarterly_balance_sheet.index:
                                total_liab = quarterly_balance_sheet.loc['Total Liabilities Net Minority Interest', date]
                            elif 'Total Liab' in quarterly_balance_sheet.index:
                                total_liab = quarterly_balance_sheet.loc['Total Liab', date]
                            
                            if 'Stockholders Equity' in quarterly_balance_sheet.index:
                                total_equity = quarterly_balance_sheet.loc['Stockholders Equity', date]
                            elif 'Total Stockholder Equity' in quarterly_balance_sheet.index:
                                total_equity = quarterly_balance_sheet.loc['Total Stockholder Equity', date]
                            
                            if 'Ordinary Shares Number' in quarterly_balance_sheet.index:
                                shares_outstanding = quarterly_balance_sheet.loc['Ordinary Shares Number', date]
                            elif 'Share Issued' in quarterly_balance_sheet.index:
                                shares_outstanding = quarterly_balance_sheet.loc['Share Issued', date]
                        
                        # Cash flow data (if available for this quarter)
                        operating_cash_flow = None
                        investing_cash_flow = None
                        financing_cash_flow = None
                        changes_in_cash = None
                        free_cash_flow = None
                        
                        if not quarterly_cash_flow.empty and date in quarterly_cash_flow.columns:
                            # Common yfinance cash flow field names with fallbacks
                            if 'Operating Cash Flow' in quarterly_cash_flow.index:
                                operating_cash_flow = quarterly_cash_flow.loc['Operating Cash Flow', date]
                            elif 'Total Cash From Operating Activities' in quarterly_cash_flow.index:
                                operating_cash_flow = quarterly_cash_flow.loc['Total Cash From Operating Activities', date]
                            
                            if 'Investing Cash Flow' in quarterly_cash_flow.index:
                                investing_cash_flow = quarterly_cash_flow.loc['Investing Cash Flow', date]
                            elif 'Total Cash From Investing Activities' in quarterly_cash_flow.index:
                                investing_cash_flow = quarterly_cash_flow.loc['Total Cash From Investing Activities', date]
                            
                            if 'Financing Cash Flow' in quarterly_cash_flow.index:
                                financing_cash_flow = quarterly_cash_flow.loc['Financing Cash Flow', date]
                            elif 'Total Cash From Financing Activities' in quarterly_cash_flow.index:
                                financing_cash_flow = quarterly_cash_flow.loc['Total Cash From Financing Activities', date]
                            
                            if 'Changes In Cash' in quarterly_cash_flow.index:
                                changes_in_cash = quarterly_cash_flow.loc['Changes In Cash', date]
                            elif 'Net Change In Cash' in quarterly_cash_flow.index:
                                changes_in_cash = quarterly_cash_flow.loc['Net Change In Cash', date]
                            
                            if 'Free Cash Flow' in quarterly_cash_flow.index:
                                free_cash_flow = quarterly_cash_flow.loc['Free Cash Flow', date]
                            elif operating_cash_flow is not None:
                                # Calculate free cash flow if not directly available
                                capex = None
                                if 'Capital Expenditures' in quarterly_cash_flow.index:
                                    capex = quarterly_cash_flow.loc['Capital Expenditures', date]
                                elif 'Capital Expenditure' in quarterly_cash_flow.index:
                                    capex = quarterly_cash_flow.loc['Capital Expenditure', date]
                                
                                if capex is not None:
                                    # CapEx is usually negative in yfinance, so we add it (subtract the absolute value)
                                    free_cash_flow = operating_cash_flow + capex
                        
                        period = FinancialPeriod(
                            date=date.to_pydatetime(),
                            total_revenue=Decimal(str(total_revenue)) if total_revenue is not None and not pd.isna(total_revenue) else None,
                            net_income=Decimal(str(net_income)) if net_income is not None and not pd.isna(net_income) else None,
                            total_assets=Decimal(str(total_assets)) if total_assets is not None and not pd.isna(total_assets) else None,
                            total_liabilities=Decimal(str(total_liab)) if total_liab is not None and not pd.isna(total_liab) else None,
                            total_equity=Decimal(str(total_equity)) if total_equity is not None and not pd.isna(total_equity) else None,
                            shares_outstanding=int(shares_outstanding) if shares_outstanding is not None and not pd.isna(shares_outstanding) else None,
                            operating_cash_flow=Decimal(str(operating_cash_flow)) if operating_cash_flow is not None and not pd.isna(operating_cash_flow) else None,
                            investing_cash_flow=Decimal(str(investing_cash_flow)) if investing_cash_flow is not None and not pd.isna(investing_cash_flow) else None,
                            financing_cash_flow=Decimal(str(financing_cash_flow)) if financing_cash_flow is not None and not pd.isna(financing_cash_flow) else None,
                            changes_in_cash=Decimal(str(changes_in_cash)) if changes_in_cash is not None and not pd.isna(changes_in_cash) else None,
                            free_cash_flow=Decimal(str(free_cash_flow)) if free_cash_flow is not None and not pd.isna(free_cash_flow) else None
                        )
                        quarterly_periods.append(period)
                        
                    except (KeyError, ValueError, TypeError) as e:
                        logger.debug(f"Error processing quarterly data for {date}: {e}")
                        continue
                
                financial_history.quarterly_periods = quarterly_periods
            
            return financial_history if (financial_history.annual_periods or financial_history.quarterly_periods) else None
            
        except Exception as e:
            logger.warning(f"Failed to calculate financial history for {self._symbol}: {e}")
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