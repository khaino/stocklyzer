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
- **Financial statements** with professional table formatting:
  - **Annual Income Statement** - Revenue and net income with growth rates
  - **Quarterly Income Statement** - Last 4 quarters of financial performance
  - **Annual Balance Sheet** - Assets, liabilities, equity, and shares outstanding
  - **Quarterly Balance Sheet** - Quarterly balance sheet analysis (when available)
  - **Annual Cash Flow Statement** - Operating, investing, financing, and free cash flow with growth rates
  - **Quarterly Cash Flow Statement** - Last 4 quarters of cash flow performance
- **Smart color coding** for financial trends:
  - Green for positive metrics (revenue growth, debt reduction, share buybacks)
  - Red for concerning trends (revenue decline, debt increase, share dilution)
  - Special logic for liabilities (red for increases, green for decreases)
  - Neutral coloring for investing and financing cash flows (both positive and negative can be strategic)
- **Cash flow analysis** with comprehensive metrics:
  - **Operating Cash Flow** - Cash generated from core business operations with growth rates
  - **Investing Cash Flow** - Cash used for investments and capital expenditures (neutral coloring)
  - **Financing Cash Flow** - Cash from financing activities like debt and dividends (neutral coloring)
  - **Changes in Cash** - Net change in cash position with growth analysis
  - **Free Cash Flow** - Operating cash flow minus capital expenditures with growth rates
  - **Automatic calculation** - Free cash flow computed when not directly available
- **High-precision formatting**:
  - Currency values with 2 decimal places for billions ($281.72B)
  - Shares outstanding with 3 decimal places (15.117B)
  - Automatic handling of missing quarterly data
