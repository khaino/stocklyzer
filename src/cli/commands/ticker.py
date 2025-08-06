"""Ticker command using service layer."""

import typer
import asyncio
from rich.console import Console

from stocklyzer.services.factory import ServiceFactory
from stocklyzer.utils.exceptions import ValidationError, StockDataError
from ..display.stock_renderer import StockRenderer

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
            # Create renderer and render stock info
            renderer = StockRenderer(console)
            renderer.render_all(stock_info)  # Currently rendering full report (existing behavior)
        else:
            console.print(f"[red]Could not fetch data for ticker: {symbol.upper()}[/red]")
            console.print("[yellow]Please check if the ticker symbol is valid.[/yellow]")
    
    except ValidationError as e:
        console.print(f"[red]Validation Error: {e}[/red]")
    except StockDataError as e:
        console.print(f"[red]Data Error: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")