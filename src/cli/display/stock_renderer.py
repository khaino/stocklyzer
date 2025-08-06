"""Stock display renderer for handling all display logic."""

from rich.console import Console
from rich.table import Table
from rich.columns import Columns

from stocklyzer.domain.models import StockInfo
from ..formatters.stock_formatter import StockDisplayFormatter
from ..formatters.financial_table_formatter import RichFinancialTableFormatter


class StockRenderer:
    """Handles all stock information rendering."""
    
    def __init__(self, console: Console):
        """Initialize the renderer with a console instance."""
        self.console = console
        self.stock_formatter = StockDisplayFormatter()
        self.table_formatter = RichFinancialTableFormatter()
    
    def render_overview(self, stock_info: StockInfo) -> None:
        """Render overview: Header + price + fundamentals + growth."""
        # Header
        self.console.print(f"\n[bold cyan]{stock_info.symbol}[/bold cyan] - "
                          f"[cyan]{stock_info.company_name}[/cyan] "
                          f"([yellow]{stock_info.get_display_classification()}[/yellow])")
        
        # Format data using formatter
        direction_symbol = self.stock_formatter.format_change_direction(stock_info)
        change_color = self.stock_formatter.format_change_color(stock_info)
        
        # Progress bar
        if stock_info.price_range:
            progress_bar = self.stock_formatter.create_progress_bar(stock_info.price_range, stock_info.current_price)
            bar_color = self.stock_formatter.get_progress_bar_color(stock_info.price_range, stock_info.current_price)
        else:
            progress_bar = "░░░░░░░░░░"
            bar_color = "dim"
        
        # Price line
        self.console.print(f"\n[bold green]Price:[/bold green] "
                          f"[cyan]${stock_info.current_price:.2f}[/cyan] "
                          f"[{change_color}]{direction_symbol} {stock_info.change_percent:+.2f}%[/{change_color}] "
                          f"   [{bar_color}][{progress_bar}][/{bar_color}] [dim]52-week range[/dim]")
        
        # Get formatted data
        fundamentals_data = self.stock_formatter.format_fundamentals_data(stock_info)
        growth_data = self.stock_formatter.format_growth_data(stock_info.growth_metrics)
        
        # Create tables
        fundamentals_table = self._create_data_table(fundamentals_data)
        growth_table = self._create_data_table(growth_data)
        
        # Create panels
        fundamentals_panel = Table(show_header=False, box=None)
        fundamentals_panel.add_column()
        fundamentals_panel.add_row("[bold yellow]📊 Fundamentals[/bold yellow]")
        fundamentals_panel.add_row(fundamentals_table)
        
        growth_panel = Table(show_header=False, box=None)
        growth_panel.add_column()
        growth_panel.add_row("[bold magenta]🚀 Growth Performance[/bold magenta]")
        growth_panel.add_row(growth_table)
        
        # Display in columns
        self.console.print(Columns([fundamentals_panel, growth_panel], equal=True, expand=False))
        self.console.print()
    
    def render_all(self, stock_info: StockInfo) -> None:
        """Render complete report - current full behavior."""
        # Render overview first
        self.render_overview(stock_info)
        
        # Check for potential data quality issues and warn user
        if stock_info.financial_history and stock_info.market_cap:
            self._check_and_warn_data_quality(stock_info)
        
        # Render financial tables if available
        if stock_info.financial_history:
            self.render_annual_income_statement(stock_info)
            self.render_quarterly_income_statement(stock_info)
            self.render_annual_balance_sheet(stock_info)
            self.render_quarterly_balance_sheet(stock_info)
            self.render_annual_cash_flow_statement(stock_info)
            self.render_quarterly_cash_flow_statement(stock_info)
    
    def render_annual_income_statement(self, stock_info: StockInfo) -> None:
        """Render annual income statement."""
        if not stock_info.financial_history:
            return
        
        annual_income_table = self.table_formatter.create_annual_income_statement_table(stock_info.financial_history)
        if annual_income_table:
            self.console.print()
            self.console.print(annual_income_table)
    
    def render_quarterly_income_statement(self, stock_info: StockInfo) -> None:
        """Render quarterly income statement."""
        if not stock_info.financial_history:
            return
        
        quarterly_income_table = self.table_formatter.create_quarterly_income_statement_table(stock_info.financial_history)
        if quarterly_income_table:
            self.console.print()
            self.console.print(quarterly_income_table)
    
    def render_annual_balance_sheet(self, stock_info: StockInfo) -> None:
        """Render annual balance sheet."""
        if not stock_info.financial_history:
            return
        
        annual_balance_sheet_table = self.table_formatter.create_annual_balance_sheet_table(stock_info.financial_history)
        if annual_balance_sheet_table:
            self.console.print()
            self.console.print(annual_balance_sheet_table)
    
    def render_quarterly_balance_sheet(self, stock_info: StockInfo) -> None:
        """Render quarterly balance sheet."""
        if not stock_info.financial_history:
            return
        
        quarterly_balance_sheet_table = self.table_formatter.create_quarterly_balance_sheet_table(stock_info.financial_history)
        if quarterly_balance_sheet_table:
            self.console.print()
            self.console.print(quarterly_balance_sheet_table)
        else:
            self.console.print()
            self.console.print("[dim]Note: Quarterly balance sheet data not available for this stock[/dim]")
    
    def render_annual_cash_flow_statement(self, stock_info: StockInfo) -> None:
        """Render annual cash flow statement."""
        if not stock_info.financial_history:
            return
        
        annual_cash_flow_table = self.table_formatter.create_annual_cash_flow_table(stock_info.financial_history)
        if annual_cash_flow_table:
            self.console.print()
            self.console.print(annual_cash_flow_table)
    
    def render_quarterly_cash_flow_statement(self, stock_info: StockInfo) -> None:
        """Render quarterly cash flow statement."""
        if not stock_info.financial_history:
            return
        
        quarterly_cash_flow_table = self.table_formatter.create_quarterly_cash_flow_table(stock_info.financial_history)
        if quarterly_cash_flow_table:
            self.console.print()
            self.console.print(quarterly_cash_flow_table)
        else:
            self.console.print()
            self.console.print("[dim]Note: Quarterly cash flow data not available for this stock[/dim]")
    
    def _create_data_table(self, data_list):
        """Create a table from list of (label, value) tuples."""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column(style="cyan", no_wrap=True, width=3)  # Tree chars
        table.add_column(style="dim", no_wrap=True, width=12)  # Labels
        table.add_column()  # Values
        
        for i, (label, value) in enumerate(data_list):
            tree_char = "└─" if i == len(data_list) - 1 else "├─"
            # Value already contains color markup from formatter
            table.add_row(tree_char, label, value)
        
        return table
    
    def _check_and_warn_data_quality(self, stock_info: StockInfo) -> None:
        """Check for potential data quality issues and warn the user."""
        if not stock_info.market_cap or stock_info.market_cap <= 0:
            return
        
        market_cap_millions = stock_info.market_cap / 1_000_000
        warnings = []
        
        # Check annual periods for suspicious data
        for period in stock_info.financial_history.annual_periods[:2]:  # Check most recent 2 years
            if period.total_revenue:
                revenue_millions = abs(float(period.total_revenue))
                if revenue_millions > market_cap_millions * 100:  # Revenue > 100x market cap
                    warnings.append(f"Annual revenue (${revenue_millions:.0f}M) seems unusually high vs market cap (${market_cap_millions:.0f}M)")
            
            if period.total_assets:
                assets_millions = abs(float(period.total_assets))
                if assets_millions > market_cap_millions * 500:  # Assets > 500x market cap
                    warnings.append(f"Annual assets (${assets_millions:.0f}M) seem unusually high vs market cap (${market_cap_millions:.0f}M)")
        
        # Check quarterly periods for suspicious data
        for period in stock_info.financial_history.quarterly_periods[:2]:  # Check most recent 2 quarters
            if period.total_revenue:
                revenue_millions = abs(float(period.total_revenue))
                if revenue_millions > market_cap_millions * 50:  # Quarterly revenue > 50x market cap
                    warnings.append(f"Quarterly revenue (${revenue_millions:.0f}M) seems unusually high vs market cap (${market_cap_millions:.0f}M)")
        
        # Display warnings if any found
        if warnings:
            self.console.print()
            self.console.print("⚠️  [yellow bold]Data Quality Warning[/yellow bold]")
            self.console.print("[yellow]The following financial data may be inaccurate (Yahoo Finance data quality issue):[/yellow]")
            for warning in warnings[:3]:  # Limit to 3 warnings to avoid spam
                self.console.print(f"[yellow]• {warning}[/yellow]")
            self.console.print("[dim]Please verify financial data from official company reports.[/dim]")