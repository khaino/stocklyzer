"""Financial statement display formatters."""

from decimal import Decimal
from typing import Optional, List
from stocklyzer.domain.models import FinancialHistory, FinancialPeriod


class FinancialTableFormatter:
    """Handles financial statement table formatting with color coding."""
    
    @staticmethod
    def format_currency_with_growth(amount: Optional[Decimal], growth: Optional[Decimal]) -> str:
        """Format currency with growth rate in compact format with color coding.
        
        Examples:
        - $391,035M(+2.0%) - Green for positive growth
        - $383,285M(-2.8%) - Red for negative growth  
        - $365,817M - Default color for base period
        """
        if amount is None:
            return "[dim]N/A[/dim]"
        
        # Format the currency amount
        currency_str = FinancialTableFormatter._format_currency(amount)
        
        # Add growth rate if available
        if growth is not None:
            if growth >= 0:
                return f"[green]{currency_str}(+{growth:.1f}%)[/green]"
            else:
                return f"[red]{currency_str}({growth:.1f}%)[/red]"
        else:
            # Base period without growth calculation
            return currency_str
    
    @staticmethod
    def _format_currency(amount: Decimal) -> str:
        """Format currency in millions/billions."""
        if amount >= 1_000:
            return f"${amount/1_000:,.0f}B"
        else:
            return f"${amount:,.0f}M"
    
    @staticmethod
    def format_date(date) -> str:
        """Format date for table headers."""
        return date.strftime("%Y-%m-%d")
    
    @staticmethod
    def format_shares_with_growth(shares_billions: float, growth: Optional[Decimal]) -> str:
        """Format shares outstanding with growth rate (opposite color coding).
        
        For shares: + is bad (dilution) = red, - is good (buybacks) = green
        """
        shares_str = f"{shares_billions:.1f}B"
        
        if growth is not None:
            if growth >= 0:
                # Positive growth (dilution) is bad = red
                return f"[red]{shares_str}(+{growth:.1f}%)[/red]"
            else:
                # Negative growth (buybacks) is good = green  
                return f"[green]{shares_str}({growth:.1f}%)[/green]"
        else:
            # Base period without growth calculation
            return shares_str
    
    @staticmethod
    def _calculate_shares_growth(periods: List) -> List[Optional[Decimal]]:
        """Calculate shares outstanding growth rates."""
        if len(periods) < 2:
            return []
        
        growth_rates = []
        
        for i in range(len(periods) - 1):
            current = periods[i].shares_outstanding      # More recent
            previous = periods[i + 1].shares_outstanding # Older period
            
            if current is not None and previous is not None and previous != 0:
                growth = ((current - previous) / previous) * 100
                growth_rates.append(Decimal(str(growth)).quantize(Decimal('0.1')))
            else:
                growth_rates.append(None)
        
        return growth_rates
    
    @staticmethod
    def format_annual_income_statement(financial_history: FinancialHistory) -> str:
        """Format annual income statement table."""
        if not financial_history.annual_periods:
            return "[dim]No annual financial data available[/dim]"
        
        periods = financial_history.annual_periods[:4]  # Show last 4 years
        revenue_growth = financial_history.get_revenue_growth("annual")
        income_growth = financial_history.get_net_income_growth("annual")
        
        # Build table header
        header = "═══════════════════ 📈 Annual Financial Statement ═══════════════════\n"
        
        # Date headers
        date_line = "                     "
        for period in periods:
            date_line += f"{FinancialTableFormatter.format_date(period.date):>18}   "
        header += date_line.rstrip() + "\n"
        
        # Total Revenue row
        revenue_line = "Total Revenue        "
        for i, period in enumerate(periods):
            growth = revenue_growth[i] if i < len(revenue_growth) else None
            formatted = FinancialTableFormatter.format_currency_with_growth(
                period.total_revenue, growth
            )
            revenue_line += f"{formatted:>18}   "
        header += revenue_line.rstrip() + "\n"
        
        # Net Income row
        income_line = "Net Income           "
        for i, period in enumerate(periods):
            growth = income_growth[i] if i < len(income_growth) else None
            formatted = FinancialTableFormatter.format_currency_with_growth(
                period.net_income, growth
            )
            income_line += f"{formatted:>18}   "
        header += income_line.rstrip()
        
        return header
    
    @staticmethod
    def format_quarterly_income_statement(financial_history: FinancialHistory) -> str:
        """Format quarterly income statement table."""
        if not financial_history.quarterly_periods:
            return "[dim]No quarterly financial data available[/dim]"
        
        periods = financial_history.quarterly_periods[:4]  # Show last 4 quarters
        revenue_growth = financial_history.get_revenue_growth("quarterly")
        income_growth = financial_history.get_net_income_growth("quarterly")
        
        # Build table header
        header = "\n═══════════════════ 📊 Quarterly Financial Statement ═══════════════\n"
        
        # Quarter headers (simplified format)
        date_line = "                     "
        for period in periods:
            quarter = f"{period.date.year}-Q{(period.date.month-1)//3 + 1}"
            date_line += f"{quarter:>18}   "
        header += date_line.rstrip() + "\n"
        
        # Total Revenue row
        revenue_line = "Total Revenue        "
        for i, period in enumerate(periods):
            growth = revenue_growth[i] if i < len(revenue_growth) else None
            formatted = FinancialTableFormatter.format_currency_with_growth(
                period.total_revenue, growth
            )
            revenue_line += f"{formatted:>18}   "
        header += revenue_line.rstrip() + "\n"
        
        # Net Income row
        income_line = "Net Income           "
        for i, period in enumerate(periods):
            growth = income_growth[i] if i < len(income_growth) else None
            formatted = FinancialTableFormatter.format_currency_with_growth(
                period.net_income, growth
            )
            income_line += f"{formatted:>18}   "
        header += income_line.rstrip()
        
        return header
    
    @staticmethod
    def format_balance_sheet_table(financial_history: FinancialHistory) -> str:
        """Format balance sheet table."""
        if not financial_history.annual_periods:
            return "[dim]No balance sheet data available[/dim]"
        
        periods = financial_history.annual_periods[:4]  # Show last 4 years
        balance_growth = financial_history.get_balance_sheet_growth()
        
        # Build table header
        header = "\n═══════════════════ 🏛️ Annual Balance Sheet ═══════════════════════\n"
        
        # Date headers
        date_line = "                     "
        for period in periods:
            date_line += f"{FinancialTableFormatter.format_date(period.date):>18}   "
        header += date_line.rstrip() + "\n"
        
        # Total Assets row
        assets_line = "Total Assets         "
        for i, period in enumerate(periods):
            growth = balance_growth["assets"][i] if i < len(balance_growth["assets"]) else None
            formatted = FinancialTableFormatter.format_currency_with_growth(
                period.total_assets, growth
            )
            assets_line += f"{formatted:>18}   "
        header += assets_line.rstrip() + "\n"
        
        # Total Liabilities row
        liab_line = "Total Liabilities    "
        for i, period in enumerate(periods):
            growth = balance_growth["liabilities"][i] if i < len(balance_growth["liabilities"]) else None
            formatted = FinancialTableFormatter.format_currency_with_growth(
                period.total_liabilities, growth
            )
            liab_line += f"{formatted:>18}   "
        header += liab_line.rstrip() + "\n"
        
        # Total Equity row
        equity_line = "Total Equity         "
        for i, period in enumerate(periods):
            growth = balance_growth["equity"][i] if i < len(balance_growth["equity"]) else None
            formatted = FinancialTableFormatter.format_currency_with_growth(
                period.total_equity, growth
            )
            equity_line += f"{formatted:>18}   "
        header += equity_line.rstrip() + "\n"
        
        # Shares Outstanding row with growth rates (opposite color coding)
        shares_growth = FinancialTableFormatter._calculate_shares_growth(periods)
        shares_line = "Shares Outstanding   "
        for i, period in enumerate(periods):
            if period.shares_outstanding:
                shares_value = period.shares_outstanding / 1_000_000_000
                growth = shares_growth[i] if i < len(shares_growth) else None
                formatted = FinancialTableFormatter.format_shares_with_growth(shares_value, growth)
            else:
                formatted = "N/A"
            shares_line += f"{formatted:>18}   "
        header += shares_line.rstrip()
        
        return header
    
    @staticmethod
    def format_quarterly_balance_sheet_table(financial_history: FinancialHistory) -> str:
        """Format quarterly balance sheet table."""
        if not financial_history.quarterly_periods:
            return "[dim]No quarterly balance sheet data available[/dim]"
        
        periods = financial_history.quarterly_periods[:4]  # Show last 4 quarters
        
        # Build table header
        header = "\n═══════════════════ 🏛️ Quarterly Balance Sheet ═══════════════════\n"
        
        # Quarter headers (simplified format)
        date_line = "                     "
        for period in periods:
            quarter = f"{period.date.year}-Q{(period.date.month-1)//3 + 1}"
            date_line += f"{quarter:>18}   "
        header += date_line.rstrip() + "\n"
        
        # Note: Most quarterly balance sheet data is not available from typical sources
        # This is a placeholder for when quarterly balance sheet data becomes available
        note_line = "[dim]Quarterly balance sheet data typically not available[/dim]"
        header += note_line
        
        return header