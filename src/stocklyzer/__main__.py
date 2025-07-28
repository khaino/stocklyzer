"""Stocklyzer is a pure library package.

This package provides stock analysis functionality and should be imported as a library.
For command-line interface, use the separate CLI package.

Example usage:
    from stocklyzer import StockAnalyzer
    analyzer = StockAnalyzer()
    info = analyzer.get_stock_info('AAPL')
    print(f"AAPL: ${info['current_price']:.2f}")
"""

# This is a library - it shouldn't be executed as a module
raise ImportError(
    "stocklyzer is a library package and cannot be executed as a module.\n"
    "For CLI functionality, use: slz --help\n"
    "For library usage: from stocklyzer import StockAnalyzer"
)
