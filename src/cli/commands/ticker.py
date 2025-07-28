"""Ticker command for CLI."""

import typer
import yfinance as yf
from rich.console import Console
from rich.table import Table

console = Console()


def display_stock_info(ticker: str, stock_data: dict):
    """Display stock information in a formatted table."""
    symbol = stock_data['symbol']
    company_name = stock_data['company_name']

    # Create a table
    table = Table(title=f"Stock Information: {symbol} ({company_name})")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    # Add rows with stock data
    table.add_row("Symbol", stock_data['symbol'])
    table.add_row("Current Price", f"${stock_data['current_price']:.2f}")

    # Color-coded change
    change = stock_data['change']
    change_percent = stock_data['change_percent']
    change_color = "green" if change >= 0 else "red"
    table.add_row("Change", f"[{change_color}]{change:+.2f}[/{change_color}]")
    table.add_row("Change %", f"[{change_color}]{change_percent:+.2f}%[/{change_color}]")

    table.add_row("Open", f"${stock_data['open']:.2f}")
    table.add_row("High", f"${stock_data['high']:.2f}")
    table.add_row("Low", f"${stock_data['low']:.2f}")
    table.add_row("Volume", f"{stock_data['volume']:,}")
    
    # Add additional info if available
    if stock_data.get('market_cap'):
        market_cap = stock_data['market_cap']
        if market_cap > 1e12:
            table.add_row("Market Cap", f"${market_cap/1e12:.2f}T")
        elif market_cap > 1e9:
            table.add_row("Market Cap", f"${market_cap/1e9:.2f}B")
        else:
            table.add_row("Market Cap", f"${market_cap/1e6:.2f}M")
    
    if stock_data.get('pe_ratio'):
        table.add_row("P/E Ratio", f"{stock_data['pe_ratio']:.2f}")
    
    if stock_data.get('sector'):
        table.add_row("Sector", stock_data['sector'])

    console.print(table)


def get_stock_data(ticker: str) -> dict:
    """Get real stock data using yfinance."""
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info
        hist = stock.history(period="2d")
        
        if hist.empty:
            return None
            
        # Get current and previous day data
        current = hist.iloc[-1]
        previous = hist.iloc[-2] if len(hist) > 1 else current
        
        # Calculate change
        current_price = float(current['Close'])
        previous_close = float(previous['Close'])
        change = current_price - previous_close
        change_percent = (change / previous_close) * 100 if previous_close > 0 else 0
        
        return {
            'symbol': ticker.upper(),
            'company_name': info.get('longName', f"{ticker.upper()} Corporation"),
            'current_price': current_price,
            'change': change,
            'change_percent': change_percent,
            'open': float(current['Open']),
            'high': float(current['High']),
            'low': float(current['Low']),
            'volume': int(current['Volume']),
            'market_cap': info.get('marketCap'),
            'pe_ratio': info.get('trailingPE'),
            'sector': info.get('sector'),
        }
        
    except Exception as e:
        console.print(f"[red]Error fetching data: {e}[/red]")
        return None


def ticker_command(symbol: str = typer.Argument(..., help="Stock ticker symbol (e.g., AAPL, MSFT)")):
    """Get real stock information for a ticker symbol using yfinance.

    Examples:
        slz ticker AAPL      # Get Apple stock info
        slz ticker MSFT      # Get Microsoft stock info
        slz ticker GOOGL     # Get Google stock info
    """
    console.print(f"[blue]Fetching real stock data for {symbol.upper()}...[/blue]")

    stock_data = get_stock_data(symbol)

    if stock_data:
        display_stock_info(symbol, stock_data)
    else:
        console.print(f"[red]Could not fetch data for ticker: {symbol.upper()}[/red]")
        console.print("[yellow]Please check if the ticker symbol is valid.[/yellow]")
