# Usage

## Command Line Interface

Get real-time stock information for any ticker symbol:

```bash
# Template
slz ticker <stock_ticker>

# Example with Apple
slz ticker AAPL

# Show help
slz --help
slz ticker --help
```

## Python API

To use Stocklyzer in a project:

```python
import stocklyzer
```

## Features

Stocklyzer provides comprehensive stock analysis including:

- **Real-time price data** from Yahoo Finance
- **Fundamental metrics** (P/E ratio, EPS, Market Cap, Book Value, Dividend Yield)
- **Growth performance** (1, 2, 3, 5, and 10-year returns)
- **Visual progress bars** for 52-week ranges
- **Dividend information** for income investors
