"""Stock information display formatters."""

from decimal import Decimal
from typing import Optional, List, Tuple
from stocklyzer.domain.models import StockInfo, GrowthMetrics, PriceRange


class StockDisplayFormatter:
    """Handles all UI formatting and rendering logic."""
    
    @staticmethod
    def format_change_direction(stock_info: StockInfo) -> str:
        """Format price change direction with UI symbols."""
        if stock_info.is_price_increasing:
            return "▲"
        elif stock_info.is_price_decreasing:
            return "▼"
        else:
            return "▶"
    
    @staticmethod
    def format_change_color(stock_info: StockInfo) -> str:
        """Get color for price change."""
        if stock_info.is_price_increasing:
            return "green"
        elif stock_info.is_price_decreasing:
            return "red"
        else:
            return "yellow"
    
    @staticmethod
    def format_market_cap(market_cap: Optional[int]) -> str:
        """Format market cap for display."""
        if not market_cap:
            return "N/A"
        
        if market_cap >= 1e12:
            return f"${market_cap/1e12:.2f}T"
        elif market_cap >= 1e9:
            return f"${market_cap/1e9:.2f}B"
        elif market_cap >= 1e6:
            return f"${market_cap/1e6:.2f}M"
        else:
            return f"${market_cap:,}"
    
    @staticmethod
    def create_progress_bar(price_range: PriceRange, current_price: Decimal, 
                          bar_length: int = 10) -> str:
        """Create visual progress bar for 52-week range."""
        if not price_range:
            return "░" * bar_length
        
        position = price_range.calculate_position_in_range(current_price)
        filled_length = int(position * bar_length)
        filled_bars = "█" * filled_length
        empty_bars = "░" * (bar_length - filled_length)
        return filled_bars + empty_bars
    
    @staticmethod
    def get_progress_bar_color(price_range: PriceRange, current_price: Decimal) -> str:
        """Get color for progress bar based on position."""
        if not price_range:
            return "dim"
        
        position = price_range.calculate_position_in_range(current_price)
        
        if position < Decimal('0.3'):
            return "bright_red"    # Bottom 30%
        elif position < Decimal('0.7'):
            return "bright_yellow" # Middle 40%
        else:
            return "bright_green"  # Top 30%
    
    @staticmethod
    def format_growth_value(growth: Optional[Decimal]) -> str:
        """Format growth percentage with color and direction."""
        if growth is None:
            return "[dim]No Data[/dim]"
        
        if growth < 0:
            return f"[red]{growth:+.2f}% ▼[/red]"
        else:
            return f"[green]{growth:+.2f}% ▲[/green]"
    
    @staticmethod
    def format_eps_value(eps: Optional[Decimal]) -> str:
        """Format EPS with proper currency formatting."""
        if eps is None:
            return "[dim]No Data[/dim]"
        
        if eps < 0:
            return f"[red]-${abs(eps):.2f}[/red]"
        else:
            return f"${eps:.2f}"
    
    @staticmethod
    def format_fundamentals_data(stock_info: StockInfo) -> List[Tuple[str, str]]:
        """Format fundamentals data for display."""
        formatter = StockDisplayFormatter()
        
        fundamentals = []
        
        # Market Cap
        fundamentals.append(("Market Cap", formatter.format_market_cap(stock_info.market_cap)))
        
        # P/E Ratio
        if stock_info.pe_ratio:
            fundamentals.append(("P/E Ratio", f"{stock_info.pe_ratio:.2f}"))
        else:
            fundamentals.append(("P/E Ratio", "[dim]No Data[/dim]"))
        
        # EPS
        fundamentals.append(("EPS (TTM)", formatter.format_eps_value(stock_info.eps)))
        
        # Book Value
        if stock_info.book_value:
            fundamentals.append(("Book Value", f"${stock_info.book_value:.2f}"))
        else:
            fundamentals.append(("Book Value", "[dim]No Data[/dim]"))
        
        return fundamentals
    
    @staticmethod
    def format_growth_data(growth_metrics: Optional[GrowthMetrics]) -> List[Tuple[str, str]]:
        """Format growth data for display."""
        formatter = StockDisplayFormatter()
        
        if not growth_metrics:
            return [
                ("1 Year", "[dim]No Data[/dim]"),
                ("2 Years", "[dim]No Data[/dim]"),
                ("5 Years", "[dim]No Data[/dim]"),
                ("10 Years", "[dim]No Data[/dim]")
            ]
        
        return [
            ("1 Year", formatter.format_growth_value(growth_metrics.one_year)),
            ("2 Years", formatter.format_growth_value(growth_metrics.two_years)),
            ("5 Years", formatter.format_growth_value(growth_metrics.five_years)),
            ("10 Years", formatter.format_growth_value(growth_metrics.ten_years))
        ]