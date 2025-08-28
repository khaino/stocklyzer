# Stocklyzer



A modern command line interface for comprehensive stock analysis

* Free software: Apache 2.0 License

## Features

* 📊 **Real-time stock data** from Yahoo Finance
* 🎨 **Clean, colorful display** with intuitive red/green coding
* 📈 **52-week range progress bar** with smart color zones
* 💰 **Comprehensive metrics** - Price, Fundamentals, Growth, Dividends, and Profit Margins
* 🚀 **Multi-year growth tracking** - 1, 2, 3, 5, and 10-year performance
* 💸 **Dividend information** - Yield percentages for income investors
* 💰 **Profit margin analysis** - Latest margin from Yahoo Finance + 1, 2, and 4-year averages
* 📋 **Financial statements** - Annual and quarterly income statements with growth rates
* 🏛️ **Balance sheet analysis** - Assets, liabilities, equity, and shares outstanding
* 💰 **Cash flow analysis** - Operating, investing, financing, and free cash flow with growth rates
* 📊 **Professional tables** - Rich table formatting with perfect alignment
* 🎯 **Smart color coding** - Green for positive metrics, red for concerning trends
* 🌈 **Terminal-friendly colors** - works on both dark and light themes
* ⚡ **Ultra-fast and minimal** - essential information only

## Installation

Clone from GitHub and install locally:

```bash
git clone https://github.com/khaino/stocklyzer.git
cd stocklyzer
pip install .[cli]
```

## Usage

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

## Visual Progress Bar

The 52-week range progress bar provides instant visual feedback:

```
Price: $524.11 ▼ -1.76%    [████████░░] 52-week range
```

- **█** (filled bars) - Show current position in 52-week range
- **░** (empty bars) - Show remaining range to 52-week high
- **Colors indicate market sentiment:**
  - 🔴 **Red bars** - Stock near 52-week lows (bearish)
  - 🟡 **Yellow bars** - Stock in middle range (neutral)
  - 🟢 **Green bars** - Stock near 52-week highs (bullish)

## Sample Output

```
slz ticker AAPL
Fetching real stock data for AAPL...

AAPL - Apple Inc. (Technology)

Price: $230.49 ▲ +0.51%    [██████░░░░] 52-week range

 📊 Fundamentals               🚀 Growth Performance              💰 Profit Margins
  ├─   Market Cap    $3.42T     ├─   1 Year        +2.24% ▲       ├─   Latest        24.3%
  ├─   P/E Ratio     35.03      ├─   2 Years       +29.17% ▲      ├─   1-Year Avg    24.0%
  ├─   EPS (TTM)     $6.58      ├─   3 Years       +45.08% ▲      ├─   2-Year Avg    24.6%
  ├─   Book Value    $4.43      ├─   5 Years       +89.86% ▲      └─   4-Year Avg    25.1%
  └─   Dividend      0.45%      └─   10 Years      +805.33% ▲  

                                       📈 Annual Financial Statement

┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Metric               ┃         2024-09-30 ┃         2023-09-30 ┃         2022-09-30 ┃         2021-09-30 ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ Total Revenue        │    $391.04B(+2.0%) │    $383.28B(-2.8%) │    $394.33B(+7.8%) │           $365.82B │
│ Net Income           │     $93.74B(-3.4%) │     $97.00B(-2.8%) │     $99.80B(+5.4%) │            $94.68B │
└──────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┘

                                           🏛️ Annual Balance Sheet
  
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Metric               ┃         2024-09-30 ┃         2023-09-30 ┃         2022-09-30 ┃         2021-09-30 ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ Total Assets         │    $364.98B(+3.5%) │     $352.58B(0.0%) │    $352.76B(+0.5%) │           $351.00B │
│ Total Liabilities    │    $308.03B(+6.1%) │    $290.44B(-3.9%) │    $302.08B(+4.9%) │           $287.91B │
│ Stockholders Equity  │     $56.95B(-8.4%) │    $62.15B(+22.6%) │    $50.67B(-19.7%) │            $63.09B │
│ Shares Outstanding   │     15.117B(-2.8%) │     15.550B(-2.5%) │     15.943B(-2.9%) │            16.427B │
└──────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┘

                                       💰 Annual Cash Flow Statement

┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Metric               ┃         2024-09-30 ┃         2023-09-30 ┃         2022-09-30 ┃         2021-09-30 ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ Operating Cash Flow  │    $118.25B(+7.0%) │    $110.54B(-9.5%) │   $122.15B(+17.4%) │           $104.04B │
│ Investing Cash Flow  │     $2.94B(-20.8%) │    $3.70B(+116.6%) │   -$22.35B(-53.7%) │           -$14.54B │
│ Financing Cash Flow  │  -$121.98B(-12.4%) │   -$108.49B(+2.0%) │  -$110.75B(-18.6%) │           -$93.35B │
│ Changes in Cash      │    -$794M(-113.8%) │    $5.76B(+152.6%) │  -$10.95B(-183.7%) │            -$3.86B │
│ Free Cash Flow       │    $108.81B(+9.3%) │    $99.58B(-10.6%) │   $111.44B(+19.9%) │            $92.95B │
└──────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┘
```

## Available Information

For each stock ticker, Stocklyzer provides:

### 📈 Price Information
- **Current Price** - Real-time stock price
- **Daily Change** - Price change with red/green color coding
- **52-Week Range Progress Bar** - Visual position in annual range
  - 🔴 **Red**: Bottom 30% (bearish zone)
  - 🟡 **Yellow**: Middle 40% (neutral zone)
  - 🟢 **Green**: Top 30% (bullish zone)

### 📊 Overview Layout
Stocklyzer displays information in a clean three-panel layout:
- **📊 Fundamentals Panel** - Market cap, P/E ratio, EPS, book value, and dividend yield
- **🚀 Growth Performance Panel** - 1, 2, 3, 5, and 10-year price performance
- **💰 Profit Margins Panel** - Latest margin and historical averages

### 📊 Fundamentals
- **Market Cap** - Total market capitalization
- **P/E Ratio** - Price-to-earnings ratio
- **EPS (TTM)** - Earnings Per Share (trailing 12 months)
- **Book Value** - Book value per share
- **Dividend** - Annual dividend yield percentage

### 🚀 Growth Performance
- **1-Year Growth** - Annual price performance
- **2-Year Growth** - Bi-annual price performance
- **3-Year Growth** - Three-year price performance
- **5-Year Growth** - Half-decade price performance
- **10-Year Growth** - Decade-long investment returns
- **Color Coding**: Red ▼ for losses, Green ▲ for gains

### 💰 Profit Margins
- **Latest Margin** - Current profit margin from Yahoo Finance (TTM)
- **1-Year Average** - Average profit margin over the last year
- **2-Year Average** - Average profit margin over the last 2 years
- **4-Year Average** - Average profit margin over the last 4 years
- **Color Coding**:
  - 🟢 **Green**: Excellent profitability (>20%)
  - 🟡 **Cyan**: Good profitability (10-20%)
  - 🟡 **Yellow**: Moderate profitability (0-10%)
  - 🔴 **Red**: Poor profitability (<0%)
- **Data Source**: Latest margin uses Yahoo Finance API, averages calculated from historical financial statements

### 📋 Financial Statements
- **Annual Income Statement** - Revenue and net income with year-over-year growth rates
- **Quarterly Income Statement** - Last 4 quarters of revenue and net income performance
- **Annual Balance Sheet** - Assets, liabilities, equity, and shares outstanding
- **Quarterly Balance Sheet** - Quarterly balance sheet metrics (when available)
- **Annual Cash Flow Statement** - Operating, investing, financing, and free cash flow with growth rates
- **Quarterly Cash Flow Statement** - Last 4 quarters of cash flow performance
- **Smart Color Coding**:
  - 🟢 **Green**: Positive trends (revenue growth, debt reduction, share buybacks)
  - 🔴 **Red**: Concerning trends (revenue decline, debt increase, share dilution)
  - **Special Logic**: Liabilities use opposite colors (red for increases, green for decreases)
  - **Neutral Coloring**: Investing and financing cash flows show no color coding as both positive and negative values can be strategic

### 💰 Cash Flow Analysis
- **Operating Cash Flow** - Cash generated from core business operations with growth rates
- **Investing Cash Flow** - Cash used for investments, acquisitions, and capital expenditures (neutral coloring)
- **Financing Cash Flow** - Cash from financing activities like debt, equity, and dividends (neutral coloring)
- **Changes in Cash** - Net change in cash position with growth analysis
- **Free Cash Flow** - Operating cash flow minus capital expenditures with growth rates
- **Automatic Calculation** - Free cash flow computed when not directly available from data source

### 🏢 Company Info
- **Company Name** - Full legal entity name
- **Sector** - Industry sector classification

## Error Handling

Invalid ticker symbols are handled gracefully:

```bash
slz ticker INVALID
Fetching real stock data for INVALID...
Could not fetch data for ticker: INVALID
Please check if the ticker symbol is valid.
```

## Development

Clone the repository and install in development mode:

```bash
git clone https://github.com/yourusername/stocklyzer.git
cd stocklyzer
pip install -e .[cli,test]
```

Run tests:

```bash
pytest tests/ -v
```

## Dependencies

- **yfinance** - For fetching real-time stock data from Yahoo Finance
- **typer** - For building the command-line interface
- **rich** - For beautiful terminal output

## Credits

This package was created with [Cookiecutter](https://github.com/audreyfeldroy/cookiecutter) and the [audreyfeldroy/cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage) project template.
