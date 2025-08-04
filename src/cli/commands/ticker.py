"""Ticker command using service layer."""

import typer
import asyncio
from rich.console import Console
from rich.table import Table
from rich.columns import Columns

from stocklyzer.services.factory import ServiceFactory
from stocklyzer.utils.exceptions import ValidationError, StockDataError
from ..formatters.stock_formatter import StockDisplayFormatter
from ..formatters.financial_table_formatter import RichFinancialTableFormatter

console = Console()


def ticker_command(symbol: str = typer.Argument(..., help="Stock ticker symbol (e.g., AAPL, MSFT)")):
    """Get comprehensive stock information with visual progress bar and growth metrics.
    
    Displays:
    - Price with 52-week range progress bar (color-coded)
    - Fundamentals: Market Cap, P/E, EPS, Book Value
    - Growth Performance: 1, 2, 5, 10-year returns
    - Red/Green color coding for losses/gains
    
    Progress Bar Colors:
    - Red: Bottom 30% of 52-week range
    - Yellow: Middle 40% of 52-week range  
    - Green: Top 30% of 52-week range

    Examples:
        slz ticker AAPL      # Get Apple stock info
        slz ticker MSFT      # Get Microsoft stock info
        slz ticker GOOGL     # Get Google stock info
    """
    asyncio.run(_handle_ticker_command(symbol))


async def _handle_ticker_command(symbol: str):
    """Handle ticker command asynchronously."""
    console.print(f"[blue]Fetching real stock data for {symbol.upper()}...[/blue]")
    
    try:
        # Create service for the specific symbol
        service = ServiceFactory.create_stock_service(symbol)
        
        # Get stock information (no symbol parameter needed)
        stock_info = await service.get_stock_info()
        
        if stock_info:
            display_stock_info(stock_info)
        else:
            console.print(f"[red]Could not fetch data for ticker: {symbol.upper()}[/red]")
            console.print("[yellow]Please check if the ticker symbol is valid.[/yellow]")
    
    except ValidationError as e:
        console.print(f"[red]Validation Error: {e}[/red]")
    except StockDataError as e:
        console.print(f"[red]Data Error: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")


def display_stock_info(stock_info):
    """Display stock information using formatters."""
    formatter = StockDisplayFormatter()
    
    # Format data using formatter
    direction_symbol = formatter.format_change_direction(stock_info)
    change_color = formatter.format_change_color(stock_info)
    
    # Progress bar
    if stock_info.price_range:
        progress_bar = formatter.create_progress_bar(stock_info.price_range, stock_info.current_price)
        bar_color = formatter.get_progress_bar_color(stock_info.price_range, stock_info.current_price)
    else:
        progress_bar = "░░░░░░░░░░"
        bar_color = "dim"
    
    # Header
    console.print(f"\n[bold cyan]{stock_info.symbol}[/bold cyan] - "
                 f"[cyan]{stock_info.company_name}[/cyan] "
                 f"([yellow]{stock_info.get_display_classification()}[/yellow])")
    
    # Price line
    console.print(f"\n[bold green]Price:[/bold green] "
                 f"[cyan]${stock_info.current_price:.2f}[/cyan] "
                 f"[{change_color}]{direction_symbol} {stock_info.change_percent:+.2f}%[/{change_color}] "
                 f"   [{bar_color}][{progress_bar}][/{bar_color}] [dim]52-week range[/dim]")
    
    # Get formatted data
    fundamentals_data = formatter.format_fundamentals_data(stock_info)
    growth_data = formatter.format_growth_data(stock_info.growth_metrics)
    
    # Create tables
    fundamentals_table = _create_data_table(fundamentals_data)
    growth_table = _create_data_table(growth_data)
    
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
    console.print(Columns([fundamentals_panel, growth_panel], equal=True, expand=False))
    
    # Check for potential data quality issues and warn user
    if stock_info.financial_history and stock_info.market_cap:
        _check_and_warn_data_quality(stock_info, console)
    
    # Display financial tables if available
    if stock_info.financial_history:
        # Create Rich tables
        annual_income_table = RichFinancialTableFormatter.create_annual_income_statement_table(stock_info.financial_history)
        quarterly_income_table = RichFinancialTableFormatter.create_quarterly_income_statement_table(stock_info.financial_history)
        annual_balance_sheet_table = RichFinancialTableFormatter.create_annual_balance_sheet_table(stock_info.financial_history)
        quarterly_balance_sheet_table = RichFinancialTableFormatter.create_quarterly_balance_sheet_table(stock_info.financial_history)
        annual_cash_flow_table = RichFinancialTableFormatter.create_annual_cash_flow_table(stock_info.financial_history)
        quarterly_cash_flow_table = RichFinancialTableFormatter.create_quarterly_cash_flow_table(stock_info.financial_history)
        
        # Display tables
        if annual_income_table:
            console.print()
            console.print(annual_income_table)
        
        if quarterly_income_table:
            console.print()
            console.print(quarterly_income_table)
        
        if annual_balance_sheet_table:
            console.print()
            console.print(annual_balance_sheet_table)
        
        if quarterly_balance_sheet_table:
            console.print()
            console.print(quarterly_balance_sheet_table)
        else:
            console.print()
            console.print("[dim]Note: Quarterly balance sheet data not available for this stock[/dim]")
        
        # Display cash flow tables
        if annual_cash_flow_table:
            console.print()
            console.print(annual_cash_flow_table)
        
        if quarterly_cash_flow_table:
            console.print()
            console.print(quarterly_cash_flow_table)
        else:
            console.print()
            console.print("[dim]Note: Quarterly cash flow data not available for this stock[/dim]")
    
    console.print()


def _check_and_warn_data_quality(stock_info, console):
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
        console.print()
        console.print("⚠️  [yellow bold]Data Quality Warning[/yellow bold]")
        console.print("[yellow]The following financial data may be inaccurate (Yahoo Finance data quality issue):[/yellow]")
        for warning in warnings[:3]:  # Limit to 3 warnings to avoid spam
            console.print(f"[yellow]• {warning}[/yellow]")
        console.print("[dim]Please verify financial data from official company reports.[/dim]")


def _create_data_table(data_list):
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