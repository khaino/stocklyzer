"""Financial statement display formatters."""

from decimal import Decimal
from typing import Dict, Optional, List
from stocklyzer.domain.models import FinancialHistory, FinancialPeriod


class FinancialTableFormatter:
    """Handles financial statement table formatting with color coding."""

    COLUMN_WIDTH = 18
    LABEL_WIDTH = 21

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
                return f"-${abs_amount / 1_000:,.0f}B"
            else:
                return f"${abs_amount / 1_000:,.0f}B"
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
            current = periods[i].shares_outstanding  # More recent
            previous = periods[i + 1].shares_outstanding  # Older period

            if current is not None and previous is not None and previous != 0:
                growth = ((current - previous) / previous) * 100
                growth_rates.append(Decimal(str(growth)).quantize(Decimal('0.1')))
            else:
                growth_rates.append(None)

        return growth_rates

    @staticmethod
    def to_label(field_name: str) -> str:
        """Convert snake_case to Title Case label."""
        return field_name.replace("_", " ").title()

    @staticmethod
    def format_header(header_text: str):
        return f"\n═══════════════════ {header_text} ═══════════════════════\n"

    @staticmethod
    def format_currency_row(periods: List[FinancialPeriod], growths: Dict[str, List[Optional[Decimal]]],
                            field_name: str):
        row_line = f"{FinancialTableFormatter.to_label(field_name)}>{FinancialTableFormatter.LABEL_WIDTH}"
        for i, period in enumerate(periods):
            growth = growths[field_name][i] if i < len(growths[field_name]) else None
            value = getattr(period, field_name)
            formatted = FinancialTableFormatter.format_currency_with_growth(value, growth)
            row_line += f"{formatted:>{FinancialTableFormatter.COLUMN_WIDTH}}"
        return row_line.rstrip()

    @staticmethod
    def format_currency_neutral_row(periods: List[FinancialPeriod], growths: Dict[str, List[Optional[Decimal]]],
                                    field_name: str):
        row_line = f"{FinancialTableFormatter.to_label(field_name)}>{FinancialTableFormatter.LABEL_WIDTH}"
        for i, period in enumerate(periods):
            growth = growths[field_name][i] if i < len(growths[field_name]) else None
            value = getattr(period, field_name)
            formatted = FinancialTableFormatter.format_currency_with_neutral_growth(value, growth)
            row_line += f"{formatted:>{FinancialTableFormatter.COLUMN_WIDTH}}"
        return row_line.rstrip()

    @staticmethod
    def format_date_row(periods: List[FinancialPeriod]):
        date_line = f"{' ':>{FinancialTableFormatter.LABEL_WIDTH}}"
        for period in periods:
            date_line += f"{FinancialTableFormatter.format_date(period.date):>{FinancialTableFormatter.COLUMN_WIDTH}}   "
        return date_line.rstrip()

    @staticmethod
    def format_quarterly_date_row(periods: List[FinancialPeriod]):
        date_line = f"{' ':>{FinancialTableFormatter.LABEL_WIDTH}}"
        for period in periods:
            quarter = f"{period.date.year}-Q{(period.date.month - 1) // 3 + 1}"
        date_line += f"{quarter:>{FinancialTableFormatter.COLUMN_WIDTH}}   "
        return date_line.rstrip()

    @staticmethod
    def format_annual_income_statement(financial_history: FinancialHistory) -> str:
        """Format annual income statement table."""
        if not financial_history.annual_periods:
            return "[dim]No annual financial data available[/dim]"

        periods = financial_history.annual_periods[:4]  # Show last 4 years
        financial_growth = financial_history.get_financial_growth("annual")

        formatted_str = FinancialTableFormatter.format_header("📈 Annual Financial Statement")
        formatted_str += FinancialTableFormatter.format_quarterly_date_row(periods)
        formatted_str += FinancialTableFormatter.format_currency_row(periods, financial_growth, "total_revenue") + "\n"
        formatted_str += FinancialTableFormatter.format_currency_row(periods, financial_growth, "net_income") + "\n"

        return formatted_str

    @staticmethod
    def format_quarterly_income_statement(financial_history: FinancialHistory) -> str:
        """Format quarterly income statement table."""
        if not financial_history.quarterly_periods:
            return "[dim]No quarterly financial data available[/dim]"

        periods = financial_history.quarterly_periods[:4]  # Show last 4 quarters
        financial_growth = financial_history.get_financial_growth("quarterly")

        formatted_str = FinancialTableFormatter.format_header("📊 Quarterly Financial Statement")
        formatted_str += FinancialTableFormatter.format_quarterly_date_row(periods)
        formatted_str += FinancialTableFormatter.format_currency_row(periods, financial_growth, "total_revenue") + "\n"
        formatted_str += FinancialTableFormatter.format_currency_row(periods, financial_growth, "net_income") + "\n"

        return formatted_str

    @staticmethod
    def format_balance_sheet_table(financial_history: FinancialHistory) -> str:
        """Format balance sheet table."""

        if not financial_history.annual_periods:
            return "[dim]No balance sheet data available[/dim]"

        periods = financial_history.annual_periods[:4]  # Show last 4 years
        balance_growth = financial_history.get_balance_sheet_growth()

        formatted_str = FinancialTableFormatter.format_header("🏛️ Annual Balance Sheet")
        formatted_str += FinancialTableFormatter.format_date_row(periods)
        formatted_str += FinancialTableFormatter.format_currency_row(periods, balance_growth, "total_assets") + "\n"
        formatted_str += FinancialTableFormatter.format_currency_row(periods, balance_growth, "total_liabilities") + "\n"
        formatted_str += FinancialTableFormatter.format_currency_row(periods, balance_growth, "total_equity") + "\n"

        # Shares Outstanding row with growth rates (opposite color coding)
        shares_growth = FinancialTableFormatter._calculate_shares_growth(periods)
        shares_line = f"Shares Outstanding>{FinancialTableFormatter.LABEL_WIDTH}"
        for i, period in enumerate(periods):
            if period.shares_outstanding:
                shares_value = period.shares_outstanding / 1_000_000_000
                growth = shares_growth[i] if i < len(shares_growth) else None
                formatted = FinancialTableFormatter.format_shares_with_growth(shares_value, growth)
            else:
                formatted = "N/A"
            shares_line += f"{formatted:>{FinancialTableFormatter.COLUMN_WIDTH}}   "
        formatted_str += shares_line.rstrip()

        return formatted_str

    @staticmethod
    def format_annual_cash_flow_statement(financial_history: FinancialHistory) -> str:
        """Format annual cash flow statement table."""
        if not financial_history.annual_periods:
            return "[dim]No annual cash flow data available[/dim]"

        periods = financial_history.annual_periods[:4]  # Show last 4 years
        cash_flow_growth = financial_history.get_cash_flow_growth("annual")

        formatted_str = FinancialTableFormatter.format_header("💰 Annual Cash Flow Statement")
        formatted_str += FinancialTableFormatter.format_date_row(periods)
        formatted_str += FinancialTableFormatter.format_currency_row(periods, cash_flow_growth, "operating_cash_flow") + "\n"
        formatted_str += FinancialTableFormatter.format_currency_neutral_row(periods, cash_flow_growth,"investing_cash_flow") + "\n"
        formatted_str += FinancialTableFormatter.format_currency_neutral_row(periods, cash_flow_growth,"financing_cash_flow") + "\n"
        formatted_str += FinancialTableFormatter.format_currency_row(periods, cash_flow_growth, "changes_in_cash") + "\n"
        formatted_str += FinancialTableFormatter.format_currency_row(periods, cash_flow_growth, "free_cash_flow") + "\n"

        return formatted_str

    @staticmethod
    def format_quarterly_cash_flow_statement(financial_history: FinancialHistory) -> str:
        """Format quarterly cash flow statement table."""
        if not financial_history.quarterly_periods:
            return "[dim]No quarterly cash flow data available[/dim]"

        periods = financial_history.quarterly_periods[:4]  # Show last 4 quarters
        cash_flow_growth = financial_history.get_cash_flow_growth("quarterly")

        formatted_str = FinancialTableFormatter.format_header("💰 Quarterly Cash Flow Statement")
        formatted_str += FinancialTableFormatter.format_quarterly_date_row(periods)
        formatted_str += FinancialTableFormatter.format_currency_row(periods, cash_flow_growth, "operating_cash_flow") + "\n"
        formatted_str += FinancialTableFormatter.format_currency_neutral_row(periods, cash_flow_growth,"investing_cash_flow") + "\n"
        formatted_str += FinancialTableFormatter.format_currency_neutral_row(periods, cash_flow_growth,"financing_cash_flow") + "\n"
        formatted_str += FinancialTableFormatter.format_currency_row(periods, cash_flow_growth, "changes_in_cash") + "\n"
        formatted_str += FinancialTableFormatter.format_currency_row(periods, cash_flow_growth, "free_cash_flow") + "\n"

        return formatted_str

    @staticmethod
    def format_quarterly_balance_sheet_table(financial_history: FinancialHistory) -> str:
        """Format quarterly balance sheet table."""
        if not financial_history.quarterly_periods:
            return "[dim]No quarterly balance sheet data available[/dim]"

        periods = financial_history.quarterly_periods[:4]  # Show last 4 quarters

        rows = FinancialTableFormatter.format_header("🏛️ Quarterly Balance Sheet")
        rows += FinancialTableFormatter.format_quarterly_date_row(periods) + "\n"

        # Note: Most quarterly balance sheet data is not available from typical sources
        # This is a placeholder for when quarterly balance sheet data becomes available
        rows += "[dim]Quarterly balance sheet data typically not available[/dim]" + "\n"

        return rows
