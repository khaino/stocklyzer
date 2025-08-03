"""Ticker command for CLI."""

import typer
import yfinance as yf
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text

console = Console()


def display_stock_info(ticker: str, stock_data: dict):
    """Display stock information in a clean, color-coded format.
    
    Features:
    - Company header with symbol, name, and sector
    - Price with 52-week range progress bar (color-coded by position)
    - Two-column layout: Fundamentals and Growth Performance
    - Red/Green color coding for negative/positive values
    - Cyan for neutral values, no white colors for terminal compatibility
    
    Args:
        ticker (str): Stock ticker symbol
        stock_data (dict): Stock data containing price, fundamentals, and growth metrics
    """
    symbol = stock_data['symbol']
    company_name = stock_data['company_name']
    
    # Header with rich colors
    console.print(f"\n[bold cyan]{symbol}[/bold cyan] - [cyan]{company_name}[/cyan] ([yellow]{stock_data.get('sector', 'Unknown')}[/yellow])")
    
    # Price section with color-coded change
    change = stock_data['change']
    change_percent = stock_data['change_percent']
    change_color = "red" if change < 0 else "green"
    arrow = "▼" if change < 0 else "▲"
    
    # Get 52-week range for progress bar
    try:
        hist_52w = yf.Ticker(ticker).history(period="1y")
        if not hist_52w.empty:
            week_52_low = float(hist_52w['Low'].min())
            week_52_high = float(hist_52w['High'].max())
            current_price = stock_data['current_price']
            
            # Calculate position in 52-week range (0-10 scale for progress bar)
            if week_52_high > week_52_low:
                position = (current_price - week_52_low) / (week_52_high - week_52_low)
                filled_bars = int(position * 10)
                progress_bar = "█" * filled_bars + "░" * (10 - filled_bars)
            else:
                progress_bar = "██████████"  # All filled if no range
        else:
            progress_bar = "░░░░░░░░░░"  # Empty if no data
            week_52_low = week_52_high = None
    except:
        progress_bar = "░░░░░░░░░░"  # Empty if error
        week_52_low = week_52_high = None
    
    # Create colored progress bar based on position
    if week_52_low and week_52_high:
        current_price = stock_data['current_price']
        position = (current_price - week_52_low) / (week_52_high - week_52_low)
        
        # Color coding suitable for both black and white terminals
        if position < 0.3:  # Bottom 30% - Bright red (visible on both backgrounds)
            bar_color = "bright_red"
        elif position < 0.7:  # Middle 40% - Bright yellow (visible on both backgrounds)
            bar_color = "bright_yellow"
        else:  # Top 30% - Bright green (visible on both backgrounds)
            bar_color = "bright_green"
    else:
        bar_color = "bright_blue"  # Default if no data
    
    console.print(f"\n[bold green]Price:[/bold green] [cyan]${stock_data['current_price']:.2f}[/cyan] [{change_color}]{arrow} {change_percent:+.2f}%[/{change_color}]    [{bar_color}][{progress_bar}][/{bar_color}] [dim]52-week range[/dim]")
    
    # Create two-column layout for Fundamentals and Growth with proper alignment
    console.print()
    
    # Prepare fundamentals data with consistent field width
    fundamentals_data = []
    if stock_data.get('market_cap'):
        market_cap = stock_data['market_cap']
        if market_cap > 1e12:
            cap_str = f"${market_cap/1e12:.2f}T"
        elif market_cap > 1e9:
            cap_str = f"${market_cap/1e9:.2f}B"
        else:
            cap_str = f"${market_cap/1e6:.2f}M"
        fundamentals_data.append(("Market Cap", cap_str))
    
    # P/E Ratio - show "No Data" if not available or negative earnings
    if stock_data.get('pe_ratio') and stock_data.get('eps', 0) > 0:
        fundamentals_data.append(("P/E Ratio", f"{stock_data['pe_ratio']:.2f}"))
    else:
        fundamentals_data.append(("P/E Ratio", "[dim]No Data[/dim]"))
    
    # EPS - always show if available, otherwise "No Data"
    if stock_data.get('eps') is not None:
        eps_value = stock_data['eps']
        if eps_value < 0:
            fundamentals_data.append(("EPS (TTM)", f"[red]${eps_value:.2f}[/red]"))
        else:
            fundamentals_data.append(("EPS (TTM)", f"${eps_value:.2f}"))
    else:
        fundamentals_data.append(("EPS (TTM)", "[dim]No Data[/dim]"))
    
    # Book Value - show "No Data" if not available
    if stock_data.get('book_value'):
        fundamentals_data.append(("Book Value", f"${stock_data['book_value']:.2f}"))
    else:
        fundamentals_data.append(("Book Value", "[dim]No Data[/dim]"))
    
    # Prepare growth data with consistent formatting
    growth_data = []
    
    def format_growth_value(growth_value):
        if growth_value is None:
            return "[dim]No Data[/dim]"
        
        # Simple red/green color coding
        if growth_value < 0:
            color = "red"
            arrow = "▼"
        else:
            color = "green"
            arrow = "▲"
        
        return f"[{color}]{growth_value:+.2f}% {arrow}[/{color}]"
    
    # Add growth data with better handling for limited history
    growth_1y = stock_data.get('growth_1y')
    growth_2y = stock_data.get('growth_2y')
    growth_5y = stock_data.get('growth_5y')
    growth_10y = stock_data.get('growth_10y')
    
    # Detect if 5Y and 10Y data are the same (indicates limited history)
    if growth_5y is not None and growth_10y is not None and abs(growth_5y - growth_10y) < 0.01:
        # Company likely has less than 5 years of history
        growth_5y = None
        growth_10y = None
    
    # Similar check for 2Y data
    if growth_2y is not None and growth_5y is not None and abs(growth_2y - growth_5y) < 0.01:
        # Company likely has less than 2 years of history
        growth_2y = None
        growth_5y = None
        growth_10y = None
    
    growth_data.append(("1 Year", format_growth_value(growth_1y)))
    growth_data.append(("2 Years", format_growth_value(growth_2y)))
    growth_data.append(("5 Years", format_growth_value(growth_5y)))
    growth_data.append(("10 Years", format_growth_value(growth_10y)))
    
    # Create two separate tables for proper alignment
    from rich.table import Table
    from rich.columns import Columns
    
    # Create fundamentals table
    fundamentals_table = Table(show_header=False, box=None, padding=(0, 1))
    fundamentals_table.add_column(style="cyan", no_wrap=True, width=3)  # Tree chars
    fundamentals_table.add_column(style="dim", no_wrap=True, width=12)  # Labels
    fundamentals_table.add_column()  # Values (will be colored cyan)
    
    # Add fundamentals data
    for i, (field, value) in enumerate(fundamentals_data):
        tree_char = "└─" if i == len(fundamentals_data) - 1 else "├─"
        fundamentals_table.add_row(tree_char, field, f"[cyan]{value}[/cyan]")
    
    # Create growth table
    growth_table = Table(show_header=False, box=None, padding=(0, 1))
    growth_table.add_column(style="cyan", no_wrap=True, width=3)  # Tree chars
    growth_table.add_column(style="dim", no_wrap=True, width=9)   # Period labels
    growth_table.add_column()  # Growth values (with color markup)
    
    # Add growth data
    for i, (period, growth_str) in enumerate(growth_data):
        tree_char = "└─" if i == len(growth_data) - 1 else "├─"
        growth_table.add_row(tree_char, period, growth_str)
    
    # Create panels with headers
    fundamentals_panel = Table(show_header=False, box=None)
    fundamentals_panel.add_column()
    fundamentals_panel.add_row("[bold yellow]📊 Fundamentals[/bold yellow]")
    fundamentals_panel.add_row(fundamentals_table)
    
    growth_panel = Table(show_header=False, box=None)
    growth_panel.add_column()
    growth_panel.add_row("[bold magenta]🚀 Growth Performance[/bold magenta]")
    growth_panel.add_row(growth_table)
    
    # Display in two aligned columns
    console.print(Columns([fundamentals_panel, growth_panel], equal=True, expand=False))
    
    console.print()  # Add spacing at the end


def get_stock_data(ticker: str) -> dict:
    """Fetch comprehensive stock data from Yahoo Finance.
    
    Retrieves real-time stock information including:
    - Current price, daily change, trading range
    - Market cap, P/E ratio, EPS (TTM and Forward)
    - Book value and price-to-book ratio
    - Multi-year growth performance (1, 2, 5, 10 years)
    
    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT')
        
    Returns:
        dict: Comprehensive stock data or None if fetch fails
    """
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

        # Get historical data for growth calculations
        def calculate_growth(start_period, end_period="1d"):
            """Calculate growth between two periods."""
            try:
                hist_start = stock.history(period=start_period)
                hist_end = stock.history(period=end_period)
                if not hist_start.empty and not hist_end.empty:
                    start_price = float(hist_start.iloc[0]['Close'])
                    end_price = float(hist_end.iloc[-1]['Close'])
                    return ((end_price - start_price) / start_price) * 100
            except (IndexError, ValueError, KeyError):
                pass
            return None

        # Calculate growth rates
        growth_1y = calculate_growth("1y")
        growth_2y = calculate_growth("2y")
        growth_5y = calculate_growth("5y")
        growth_10y = calculate_growth("10y")

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
            # New financial metrics
            'eps': info.get('trailingEps'),  # Earnings Per Share (trailing 12 months)
            'eps_forward': info.get('forwardEps'),  # Forward EPS
            'book_value': info.get('bookValue'),  # Book Value per Share
            'price_to_book': info.get('priceToBook'),  # Price-to-Book ratio
            'growth_1y': growth_1y,  # 1-year price growth
            'growth_2y': growth_2y,  # 2-year price growth
            'growth_5y': growth_5y,  # 5-year price growth
            'growth_10y': growth_10y,  # 10-year price growth
        }

    except Exception as e:
        console.print(f"[red]Error fetching data: {e}[/red]")
        return None


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
    console.print(f"[blue]Fetching real stock data for {symbol.upper()}...[/blue]")

    stock_data = get_stock_data(symbol)

    if stock_data:
        display_stock_info(symbol, stock_data)
    else:
        console.print(f"[red]Could not fetch data for ticker: {symbol.upper()}[/red]")
        console.print("[yellow]Please check if the ticker symbol is valid.[/yellow]")
