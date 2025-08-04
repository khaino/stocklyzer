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
                growth_str = FinancialTableFormatter._format_percentage(growth)
                return f"[green]{currency_str}(+{growth_str})[/green]"
            else:
                growth_str = FinancialTableFormatter._format_percentage(growth)
                return f"[red]{currency_str}({growth_str})[/red]"
        else:
            # Base period without growth calculation
            return currency_str
    
    @staticmethod
    def format_currency_with_neutral_growth(amount: Optional[Decimal], growth: Optional[Decimal]) -> str:
        """Format currency with growth rate but no color coding."""
        if amount is None:
            return "[dim]N/A[/dim]"
        
        # Format the currency amount
        currency_str = FinancialTableFormatter._format_currency(amount)
        
        # Add growth rate if available (without color coding)
        if growth is not None:
            if growth >= 0:
                growth_str = FinancialTableFormatter._format_percentage(growth)
                return f"{currency_str}(+{growth_str})"
            else:
                growth_str = FinancialTableFormatter._format_percentage(growth)
                return f"{currency_str}({growth_str})"
        else:
            # Base period without growth calculation
            return currency_str
    
    @staticmethod
    def _format_percentage(growth: Decimal) -> str:
        """Format percentage, using 'k' for values over 999%."""
        abs_growth = abs(growth)
        if abs_growth > 999:
            # Use 'k' for thousands when percentage is over 999%
            k_value = abs_growth / 1000
            return f"{k_value:.1f}k%"
        else:
            return f"{growth:.1f}%"
    
    @staticmethod
    def _format_currency(amount: Decimal) -> str:
        """Format currency in millions/billions with proper negative sign placement."""
        abs_amount = abs(amount)
        if abs_amount >= 1_000:
            if amount < 0:
                return f"-${abs_amount/1_000:,.0f}B"
            else:
                return f"${abs_amount/1_000:,.0f}B"
        else:
            if amount < 0:
                return f"-${abs_amount:,.0f}M"
            else:
                return f"${abs_amount:,.0f}M"
    
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
                growth_str = FinancialTableFormatter._format_percentage(growth)
                return f"[red]{shares_str}(+{growth_str})[/red]"
            else:
                # Negative growth (buybacks) is good = green  
                growth_str = FinancialTableFormatter._format_percentage(growth)
                return f"[green]{shares_str}({growth_str})[/green]"
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
    def format_annual_cash_flow_statement(financial_history: FinancialHistory) -> str:
        """Format annual cash flow statement table."""
        if not financial_history.annual_periods:
            return "[dim]No annual cash flow data available[/dim]"
        
        periods = financial_history.annual_periods[:4]  # Show last 4 years
        cash_flow_growth = financial_history.get_cash_flow_growth("annual")
        
        # Build table header
        header = "\n═══════════════════ 💰 Annual Cash Flow Statement ═══════════════════\n"
        
        # Date headers
        date_line = "                     "
        for period in periods:
            date_line += f"{FinancialTableFormatter.format_date(period.date):>18}   "
        header += date_line.rstrip() + "\n"
        
        # Operating Cash Flow row
        operating_line = "Operating Cash Flow  "
        for i, period in enumerate(periods):
            growth = cash_flow_growth["operating_cash_flow"][i] if i < len(cash_flow_growth["operating_cash_flow"]) else None
            formatted = FinancialTableFormatter.format_currency_with_growth(
                period.operating_cash_flow, growth
            )
            operating_line += f"{formatted:>18}   "
        header += operating_line.rstrip() + "\n"
        
        # Investing Cash Flow row (neutral coloring)
        investing_line = "Investing Cash Flow  "
        for i, period in enumerate(periods):
            growth = cash_flow_growth["investing_cash_flow"][i] if i < len(cash_flow_growth["investing_cash_flow"]) else None
            formatted = FinancialTableFormatter.format_currency_with_neutral_growth(
                period.investing_cash_flow, growth
            )
            investing_line += f"{formatted:>18}   "
        header += investing_line.rstrip() + "\n"
        
        # Financing Cash Flow row (neutral coloring)
        financing_line = "Financing Cash Flow  "
        for i, period in enumerate(periods):
            growth = cash_flow_growth["financing_cash_flow"][i] if i < len(cash_flow_growth["financing_cash_flow"]) else None
            formatted = FinancialTableFormatter.format_currency_with_neutral_growth(
                period.financing_cash_flow, growth
            )
            financing_line += f"{formatted:>18}   "
        header += financing_line.rstrip() + "\n"
        
        # Changes in Cash row
        changes_line = "Changes in Cash      "
        for i, period in enumerate(periods):
            growth = cash_flow_growth["changes_in_cash"][i] if i < len(cash_flow_growth["changes_in_cash"]) else None
            formatted = FinancialTableFormatter.format_currency_with_growth(
                period.changes_in_cash, growth
            )
            changes_line += f"{formatted:>18}   "
        header += changes_line.rstrip() + "\n"
        
        # Free Cash Flow row
        free_cf_line = "Free Cash Flow       "
        for i, period in enumerate(periods):
            growth = cash_flow_growth["free_cash_flow"][i] if i < len(cash_flow_growth["free_cash_flow"]) else None
            formatted = FinancialTableFormatter.format_currency_with_growth(
                period.free_cash_flow, growth
            )
            free_cf_line += f"{formatted:>18}   "
        header += free_cf_line.rstrip()
        
        return header
    
    @staticmethod
    def format_quarterly_cash_flow_statement(financial_history: FinancialHistory) -> str:
        """Format quarterly cash flow statement table."""
        if not financial_history.quarterly_periods:
            return "[dim]No quarterly cash flow data available[/dim]"
        
        periods = financial_history.quarterly_periods[:4]  # Show last 4 quarters
        cash_flow_growth = financial_history.get_cash_flow_growth("quarterly")
        
        # Build table header
        header = "\n═══════════════════ 💰 Quarterly Cash Flow Statement ═══════════════\n"
        
        # Quarter headers (simplified format)
        date_line = "                     "
        for period in periods:
            quarter = f"{period.date.year}-Q{(period.date.month-1)//3 + 1}"
            date_line += f"{quarter:>18}   "
        header += date_line.rstrip() + "\n"
        
        # Operating Cash Flow row
        operating_line = "Operating Cash Flow  "
        for i, period in enumerate(periods):
            growth = cash_flow_growth["operating_cash_flow"][i] if i < len(cash_flow_growth["operating_cash_flow"]) else None
            formatted = FinancialTableFormatter.format_currency_with_growth(
                period.operating_cash_flow, growth
            )
            operating_line += f"{formatted:>18}   "
        header += operating_line.rstrip() + "\n"
        
        # Investing Cash Flow row (neutral coloring)
        investing_line = "Investing Cash Flow  "
        for i, period in enumerate(periods):
            growth = cash_flow_growth["investing_cash_flow"][i] if i < len(cash_flow_growth["investing_cash_flow"]) else None
            formatted = FinancialTableFormatter.format_currency_with_neutral_growth(
                period.investing_cash_flow, growth
            )
            investing_line += f"{formatted:>18}   "
        header += investing_line.rstrip() + "\n"
        
        # Financing Cash Flow row (neutral coloring)
        financing_line = "Financing Cash Flow  "
        for i, period in enumerate(periods):
            growth = cash_flow_growth["financing_cash_flow"][i] if i < len(cash_flow_growth["financing_cash_flow"]) else None
            formatted = FinancialTableFormatter.format_currency_with_neutral_growth(
                period.financing_cash_flow, growth
            )
            financing_line += f"{formatted:>18}   "
        header += financing_line.rstrip() + "\n"
        
        # Changes in Cash row
        changes_line = "Changes in Cash      "
        for i, period in enumerate(periods):
            growth = cash_flow_growth["changes_in_cash"][i] if i < len(cash_flow_growth["changes_in_cash"]) else None
            formatted = FinancialTableFormatter.format_currency_with_growth(
                period.changes_in_cash, growth
            )
            changes_line += f"{formatted:>18}   "
        header += changes_line.rstrip() + "\n"
        
        # Free Cash Flow row
        free_cf_line = "Free Cash Flow       "
        for i, period in enumerate(periods):
            growth = cash_flow_growth["free_cash_flow"][i] if i < len(cash_flow_growth["free_cash_flow"]) else None
            formatted = FinancialTableFormatter.format_currency_with_growth(
                period.free_cash_flow, growth
            )
            free_cf_line += f"{formatted:>18}   "
        header += free_cf_line.rstrip()
        
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