"""Rich table-based financial statement formatters for better alignment."""

from decimal import Decimal
from typing import Optional, List
from rich.table import Table
from rich.console import Console
from stocklyzer.domain.models import FinancialHistory, FinancialPeriod


class RichFinancialTableFormatter:
    """Rich table-based formatter for perfect alignment and professional look."""
    
    @staticmethod
    def create_annual_income_statement_table(financial_history: FinancialHistory) -> Table:
        """Create a Rich table for annual income statement."""
        if not financial_history.annual_periods:
            return None
        
        periods = financial_history.annual_periods[:4]  # Show last 4 years
        revenue_growth = financial_history.get_revenue_growth("annual")
        income_growth = financial_history.get_net_income_growth("annual")
        
        # Create table
        table = Table(title="📈 Annual Financial Statement", show_header=True, header_style="bold cyan")
        
        # Add columns
        table.add_column("Metric", style="cyan", no_wrap=True, width=20)
        for period in periods:
            table.add_column(period.date.strftime("%Y-%m-%d"), justify="right", width=18)
        
        # Add revenue row
        revenue_row = ["Total Revenue"]
        for i, period in enumerate(periods):
            growth = revenue_growth[i] if i < len(revenue_growth) else None
            formatted = RichFinancialTableFormatter._format_currency_with_growth(
                period.total_revenue, growth
            )
            revenue_row.append(formatted)
        table.add_row(*revenue_row)
        
        # Add net income row
        income_row = ["Net Income"]
        for i, period in enumerate(periods):
            growth = income_growth[i] if i < len(income_growth) else None
            formatted = RichFinancialTableFormatter._format_currency_with_growth(
                period.net_income, growth
            )
            income_row.append(formatted)
        table.add_row(*income_row)
        
        return table
    
    @staticmethod
    def create_annual_balance_sheet_table(financial_history: FinancialHistory) -> Table:
        """Create a Rich table for annual balance sheet."""
        if not financial_history.annual_periods:
            return None
        
        periods = financial_history.annual_periods[:4]  # Show last 4 years
        balance_growth = financial_history.get_balance_sheet_growth()
        shares_growth = RichFinancialTableFormatter._calculate_shares_growth(periods)
        
        # Create table
        table = Table(title="🏛️ Annual Balance Sheet", show_header=True, header_style="bold cyan")
        
        # Add columns
        table.add_column("Metric", style="cyan", no_wrap=True, width=20)
        for period in periods:
            table.add_column(period.date.strftime("%Y-%m-%d"), justify="right", width=18)
        
        # Add assets row
        assets_row = ["Total Assets"]
        for i, period in enumerate(periods):
            growth = balance_growth["assets"][i] if i < len(balance_growth["assets"]) else None
            formatted = RichFinancialTableFormatter._format_currency_with_growth(
                period.total_assets, growth
            )
            assets_row.append(formatted)
        table.add_row(*assets_row)
        
        # Add liabilities row
        liab_row = ["Total Liabilities"]
        for i, period in enumerate(periods):
            growth = balance_growth["liabilities"][i] if i < len(balance_growth["liabilities"]) else None
            formatted = RichFinancialTableFormatter._format_liabilities_with_growth(
                period.total_liabilities, growth
            )
            liab_row.append(formatted)
        table.add_row(*liab_row)
        
        # Add equity row
        equity_row = ["Stockholders Equity"]
        for i, period in enumerate(periods):
            growth = balance_growth["equity"][i] if i < len(balance_growth["equity"]) else None
            formatted = RichFinancialTableFormatter._format_currency_with_growth(
                period.total_equity, growth
            )
            equity_row.append(formatted)
        table.add_row(*equity_row)
        
        # Add shares outstanding row (with opposite color coding)
        shares_row = ["Shares Outstanding"]
        for i, period in enumerate(periods):
            if period.shares_outstanding:
                shares_value = period.shares_outstanding / 1_000_000_000
                growth = shares_growth[i] if i < len(shares_growth) else None
                formatted = RichFinancialTableFormatter._format_shares_with_growth(shares_value, growth)
            else:
                formatted = "N/A"
            shares_row.append(formatted)
        table.add_row(*shares_row)
        
        return table
    
    @staticmethod
    def create_quarterly_income_statement_table(financial_history: FinancialHistory) -> Table:
        """Create a Rich table for quarterly income statement."""
        if not financial_history.quarterly_periods:
            return None
        
        periods = financial_history.quarterly_periods[:4]  # Show last 4 quarters
        revenue_growth = financial_history.get_revenue_growth("quarterly")
        income_growth = financial_history.get_net_income_growth("quarterly")
        
        # Create table
        table = Table(title="📊 Quarterly Financial Statement", show_header=True, header_style="bold cyan")
        
        # Add columns
        table.add_column("Metric", style="cyan", no_wrap=True, width=20)
        for period in periods:
            quarter = f"{period.date.year}-Q{(period.date.month-1)//3 + 1}"
            table.add_column(quarter, justify="right", width=18)
        
        # Add revenue row
        revenue_row = ["Total Revenue"]
        for i, period in enumerate(periods):
            growth = revenue_growth[i] if i < len(revenue_growth) else None
            formatted = RichFinancialTableFormatter._format_currency_with_growth(
                period.total_revenue, growth
            )
            revenue_row.append(formatted)
        table.add_row(*revenue_row)
        
        # Add net income row
        income_row = ["Net Income"]
        for i, period in enumerate(periods):
            growth = income_growth[i] if i < len(income_growth) else None
            formatted = RichFinancialTableFormatter._format_currency_with_growth(
                period.net_income, growth
            )
            income_row.append(formatted)
        table.add_row(*income_row)
        
        return table
    
    @staticmethod
    def create_quarterly_balance_sheet_table(financial_history: FinancialHistory) -> Table:
        """Create a Rich table for quarterly balance sheet."""
        if not financial_history.quarterly_periods:
            return None
        
        # Filter out periods with missing balance sheet data and take up to 4 quarters
        valid_periods = []
        for period in financial_history.quarterly_periods:
            if (period.total_assets is not None or 
                period.total_liabilities is not None or 
                period.total_equity is not None or 
                period.shares_outstanding is not None):
                valid_periods.append(period)
            if len(valid_periods) >= 4:
                break
        
        if not valid_periods:
            return None
        
        periods = valid_periods[:4]  # Show last 4 quarters with data
        
        # Calculate balance sheet growth rates for valid periods only
        balance_growth = {
            "assets": RichFinancialTableFormatter._calculate_growth_rates(periods, "total_assets"),
            "liabilities": RichFinancialTableFormatter._calculate_growth_rates(periods, "total_liabilities"),
            "equity": RichFinancialTableFormatter._calculate_growth_rates(periods, "total_equity")
        }
        shares_growth = RichFinancialTableFormatter._calculate_shares_growth(periods)
        
        # Create table
        table = Table(title="🏛️ Quarterly Balance Sheet", show_header=True, header_style="bold cyan")
        
        # Add columns
        table.add_column("Metric", style="cyan", no_wrap=True, width=20)
        for period in periods:
            quarter = f"{period.date.year}-Q{(period.date.month-1)//3 + 1}"
            table.add_column(quarter, justify="right", width=18)
        
        # Add assets row
        assets_row = ["Total Assets"]
        for i, period in enumerate(periods):
            growth = balance_growth["assets"][i] if i < len(balance_growth["assets"]) else None
            formatted = RichFinancialTableFormatter._format_currency_with_growth(
                period.total_assets, growth
            )
            assets_row.append(formatted)
        table.add_row(*assets_row)
        
        # Add liabilities row
        liab_row = ["Total Liabilities"]
        for i, period in enumerate(periods):
            growth = balance_growth["liabilities"][i] if i < len(balance_growth["liabilities"]) else None
            formatted = RichFinancialTableFormatter._format_liabilities_with_growth(
                period.total_liabilities, growth
            )
            liab_row.append(formatted)
        table.add_row(*liab_row)
        
        # Add equity row
        equity_row = ["Stockholders Equity"]
        for i, period in enumerate(periods):
            growth = balance_growth["equity"][i] if i < len(balance_growth["equity"]) else None
            formatted = RichFinancialTableFormatter._format_currency_with_growth(
                period.total_equity, growth
            )
            equity_row.append(formatted)
        table.add_row(*equity_row)
        
        # Add shares outstanding row (with opposite color coding)
        shares_row = ["Shares Outstanding"]
        for i, period in enumerate(periods):
            if period.shares_outstanding:
                shares_value = period.shares_outstanding / 1_000_000_000
                growth = shares_growth[i] if i < len(shares_growth) else None
                formatted = RichFinancialTableFormatter._format_shares_with_growth(shares_value, growth)
            else:
                formatted = "[dim]N/A[/dim]"
            shares_row.append(formatted)
        table.add_row(*shares_row)
        
        return table
    
    @staticmethod
    def create_annual_cash_flow_table(financial_history: FinancialHistory) -> Table:
        """Create a Rich table for annual cash flow statement."""
        if not financial_history.annual_periods:
            return None
        
        periods = financial_history.annual_periods[:4]  # Show last 4 years
        cash_flow_growth = financial_history.get_cash_flow_growth("annual")
        
        # Create table
        table = Table(title="💰 Annual Cash Flow Statement", show_header=True, header_style="bold cyan")
        
        # Add columns
        table.add_column("Metric", style="cyan", no_wrap=True, width=20)
        for period in periods:
            table.add_column(period.date.strftime("%Y-%m-%d"), justify="right", width=18)
        
        # Add operating cash flow row
        operating_row = ["Operating Cash Flow"]
        for i, period in enumerate(periods):
            growth = cash_flow_growth["operating_cash_flow"][i] if i < len(cash_flow_growth["operating_cash_flow"]) else None
            formatted = RichFinancialTableFormatter._format_currency_with_growth(
                period.operating_cash_flow, growth
            )
            operating_row.append(formatted)
        table.add_row(*operating_row)
        
        # Add investing cash flow row (neutral coloring)
        investing_row = ["Investing Cash Flow"]
        for i, period in enumerate(periods):
            growth = cash_flow_growth["investing_cash_flow"][i] if i < len(cash_flow_growth["investing_cash_flow"]) else None
            formatted = RichFinancialTableFormatter._format_currency_with_neutral_growth(
                period.investing_cash_flow, growth
            )
            investing_row.append(formatted)
        table.add_row(*investing_row)
        
        # Add financing cash flow row (neutral coloring)
        financing_row = ["Financing Cash Flow"]
        for i, period in enumerate(periods):
            growth = cash_flow_growth["financing_cash_flow"][i] if i < len(cash_flow_growth["financing_cash_flow"]) else None
            formatted = RichFinancialTableFormatter._format_currency_with_neutral_growth(
                period.financing_cash_flow, growth
            )
            financing_row.append(formatted)
        table.add_row(*financing_row)
        
        # Add changes in cash row
        changes_row = ["Changes in Cash"]
        for i, period in enumerate(periods):
            growth = cash_flow_growth["changes_in_cash"][i] if i < len(cash_flow_growth["changes_in_cash"]) else None
            formatted = RichFinancialTableFormatter._format_currency_with_growth(
                period.changes_in_cash, growth
            )
            changes_row.append(formatted)
        table.add_row(*changes_row)
        
        # Add free cash flow row
        free_cf_row = ["Free Cash Flow"]
        for i, period in enumerate(periods):
            growth = cash_flow_growth["free_cash_flow"][i] if i < len(cash_flow_growth["free_cash_flow"]) else None
            formatted = RichFinancialTableFormatter._format_currency_with_growth(
                period.free_cash_flow, growth
            )
            free_cf_row.append(formatted)
        table.add_row(*free_cf_row)
        
        return table
    
    @staticmethod
    def create_quarterly_cash_flow_table(financial_history: FinancialHistory) -> Table:
        """Create a Rich table for quarterly cash flow statement."""
        if not financial_history.quarterly_periods:
            return None
        
        periods = financial_history.quarterly_periods[:4]  # Show last 4 quarters
        cash_flow_growth = financial_history.get_cash_flow_growth("quarterly")
        
        # Create table
        table = Table(title="💰 Quarterly Cash Flow Statement", show_header=True, header_style="bold cyan")
        
        # Add columns
        table.add_column("Metric", style="cyan", no_wrap=True, width=20)
        for period in periods:
            quarter = f"{period.date.year}-Q{(period.date.month-1)//3 + 1}"
            table.add_column(quarter, justify="right", width=18)
        
        # Add operating cash flow row
        operating_row = ["Operating Cash Flow"]
        for i, period in enumerate(periods):
            growth = cash_flow_growth["operating_cash_flow"][i] if i < len(cash_flow_growth["operating_cash_flow"]) else None
            formatted = RichFinancialTableFormatter._format_currency_with_growth(
                period.operating_cash_flow, growth
            )
            operating_row.append(formatted)
        table.add_row(*operating_row)
        
        # Add investing cash flow row (neutral coloring)
        investing_row = ["Investing Cash Flow"]
        for i, period in enumerate(periods):
            growth = cash_flow_growth["investing_cash_flow"][i] if i < len(cash_flow_growth["investing_cash_flow"]) else None
            formatted = RichFinancialTableFormatter._format_currency_with_neutral_growth(
                period.investing_cash_flow, growth
            )
            investing_row.append(formatted)
        table.add_row(*investing_row)
        
        # Add financing cash flow row (neutral coloring)
        financing_row = ["Financing Cash Flow"]
        for i, period in enumerate(periods):
            growth = cash_flow_growth["financing_cash_flow"][i] if i < len(cash_flow_growth["financing_cash_flow"]) else None
            formatted = RichFinancialTableFormatter._format_currency_with_neutral_growth(
                period.financing_cash_flow, growth
            )
            financing_row.append(formatted)
        table.add_row(*financing_row)
        
        # Add changes in cash row
        changes_row = ["Changes in Cash"]
        for i, period in enumerate(periods):
            growth = cash_flow_growth["changes_in_cash"][i] if i < len(cash_flow_growth["changes_in_cash"]) else None
            formatted = RichFinancialTableFormatter._format_currency_with_growth(
                period.changes_in_cash, growth
            )
            changes_row.append(formatted)
        table.add_row(*changes_row)
        
        # Add free cash flow row
        free_cf_row = ["Free Cash Flow"]
        for i, period in enumerate(periods):
            growth = cash_flow_growth["free_cash_flow"][i] if i < len(cash_flow_growth["free_cash_flow"]) else None
            formatted = RichFinancialTableFormatter._format_currency_with_growth(
                period.free_cash_flow, growth
            )
            free_cf_row.append(formatted)
        table.add_row(*free_cf_row)
        
        return table
    
    @staticmethod
    def _format_currency_with_growth(amount: Optional[Decimal], growth: Optional[Decimal]) -> str:
        """Format currency with growth rate and color coding."""
        if amount is None:
            return "[dim]N/A[/dim]"
        
        # Format the currency amount with proper negative sign placement
        abs_amount = abs(amount)
        if abs_amount >= 1_000:
            if amount < 0:
                currency_str = f"-${abs_amount/1_000:,.2f}B"
            else:
                currency_str = f"${abs_amount/1_000:,.2f}B"
        else:
            if amount < 0:
                currency_str = f"-${abs_amount:,.0f}M"
            else:
                currency_str = f"${abs_amount:,.0f}M"
        
        # Add growth rate if available
        if growth is not None:
            # Handle the special case of -0.0 which should be treated as 0.0
            if growth == 0:
                return f"{currency_str}(0.0%)"
            elif growth > 0:
                return f"[green]{currency_str}(+{growth:.1f}%)[/green]"
            else:
                return f"[red]{currency_str}({growth:.1f}%)[/red]"
        else:
            # Base period without growth calculation, or growth not meaningful
            return currency_str
    
    @staticmethod
    def _format_currency_with_neutral_growth(amount: Optional[Decimal], growth: Optional[Decimal]) -> str:
        """Format currency with growth rate but no color coding."""
        if amount is None:
            return "[dim]N/A[/dim]"
        
        # Format the currency amount with proper negative sign placement
        abs_amount = abs(amount)
        if abs_amount >= 1_000:
            if amount < 0:
                currency_str = f"-${abs_amount/1_000:,.2f}B"
            else:
                currency_str = f"${abs_amount/1_000:,.2f}B"
        else:
            if amount < 0:
                currency_str = f"-${abs_amount:,.0f}M"
            else:
                currency_str = f"${abs_amount:,.0f}M"
        
        # Add growth rate if available (without color coding)
        if growth is not None:
            # Handle the special case of -0.0 which should be treated as 0.0
            if growth == 0:
                return f"{currency_str}(0.0%)"
            elif growth > 0:
                return f"{currency_str}(+{growth:.1f}%)"
            else:
                return f"{currency_str}({growth:.1f}%)"
        else:
            # Base period without growth calculation, or growth not meaningful
            return currency_str
    
    @staticmethod
    def _format_shares_with_growth(shares_billions: float, growth: Optional[Decimal]) -> str:
        """Format shares outstanding with growth rate (opposite color coding)."""
        shares_str = f"{shares_billions:.3f}B"
        
        if growth is not None:
            # Handle the special case of -0.0 which should be treated as 0.0
            if growth == 0:
                return f"{shares_str}(0.0%)"
            elif growth > 0:
                # Positive growth (dilution) is bad = red
                return f"[red]{shares_str}(+{growth:.1f}%)[/red]"
            else:
                # Negative growth (buybacks) is good = green  
                return f"[green]{shares_str}({growth:.1f}%)[/green]"
        else:
            # Base period without growth calculation
            return shares_str
    
    @staticmethod
    def _calculate_shares_growth(periods: List[FinancialPeriod]) -> List[Optional[Decimal]]:
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
    def _calculate_growth_rates(periods: List, metric: str) -> List[Optional[Decimal]]:
        """Calculate period-over-period growth rates for any metric with proper handling for negative base values."""
        if len(periods) < 2:
            return []
        
        growth_rates = []
        for i in range(len(periods) - 1):
            current = getattr(periods[i], metric)
            previous = getattr(periods[i + 1], metric)
            if current is not None and previous is not None and previous != 0:
                # Use absolute value of denominator for meaningful percentage when base is negative
                growth = ((current - previous) / abs(previous)) * 100
                growth_rates.append(Decimal(str(growth)).quantize(Decimal('0.1')))
            else:
                growth_rates.append(None)
        return growth_rates
    
    @staticmethod
    def _format_liabilities_with_growth(amount: Optional[Decimal], growth: Optional[Decimal]) -> str:
        """Format liabilities with growth rate and OPPOSITE color coding (green for decrease, red for increase)."""
        if amount is None:
            return "[dim]N/A[/dim]"
        
        # Format the currency amount with proper negative sign placement
        abs_amount = abs(amount)
        if abs_amount >= 1_000:
            if amount < 0:
                currency_str = f"-${abs_amount/1_000:,.2f}B"
            else:
                currency_str = f"${abs_amount/1_000:,.2f}B"
        else:
            if amount < 0:
                currency_str = f"-${abs_amount:,.0f}M"
            else:
                currency_str = f"${abs_amount:,.0f}M"
        
        # Add growth rate if available (OPPOSITE colors for liabilities)
        if growth is not None:
            # Handle the special case of -0.0 which should be treated as 0.0
            if growth == 0:
                return f"{currency_str}(0.0%)"
            elif growth > 0:
                # Positive growth in liabilities is bad = red
                return f"[red]{currency_str}(+{growth:.1f}%)[/red]"
            else:
                # Negative growth in liabilities is good = green
                return f"[green]{currency_str}({growth:.1f}%)[/green]"
        else:
            # Base period without growth calculation, or growth not meaningful
            return currency_str