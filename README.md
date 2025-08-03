# Stocklyzer



A modern command line interface for comprehensive stock analysis

* Free software: Apache 2.0 License

## Features

* 📊 **Real-time stock data** from Yahoo Finance
* 🎨 **Clean, colorful display** with intuitive red/green coding
* 📈 **52-week range progress bar** with smart color zones
* 💰 **Comprehensive metrics** - Price, Fundamentals, and Growth
* 🚀 **Multi-year growth tracking** - 1, 2, 5, and 10-year performance
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
# Get Apple stock info
slz ticker AAPL

# Get Microsoft stock info  
slz ticker MSFT

# Get Google stock info
slz ticker GOOGL

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

### Apple Inc. (AAPL)
```
slz ticker AAPL
Fetching real stock data for AAPL...

AAPL - Apple Inc. (Technology)

Price: $202.38 ▼ -2.50%    [███░░░░░░░] 52-week range

 📊 Fundamentals               🚀 Growth Performance        
  ├─   Market Cap    $3.00T     ├─   1 Year     -7.52% ▼    
  ├─   P/E Ratio     30.66      ├─   2 Years    +6.14% ▲    
  ├─   EPS (TTM)     $6.60      ├─   5 Years    +91.11% ▲   
  └─   Book Value    $4.43      └─   10 Years   +662.93% ▲  
```

### Microsoft Corporation (MSFT)
```
slz ticker MSFT
Fetching real stock data for MSFT...

MSFT - Microsoft Corporation (Technology)

Price: $524.11 ▼ -1.76%    [████████░░] 52-week range

 📊 Fundamentals               🚀 Growth Performance         
  ├─   Market Cap    $3.90T     ├─   1 Year     +29.29% ▲    
  ├─   P/E Ratio     38.45      ├─   2 Years    +62.52% ▲    
  ├─   EPS (TTM)     $13.63     ├─   5 Years    +152.63% ▲   
  └─   Book Value    $46.20     └─   10 Years   +1191.28% ▲  
```

### Alphabet Inc. (GOOGL)
```
slz ticker GOOGL
Fetching real stock data for GOOGL...

GOOGL - Alphabet Inc. (Communication Services)

Price: $189.13 ▼ -1.44%    [███████░░░] 52-week range

 📊 Fundamentals               🚀 Growth Performance        
  ├─   Market Cap    $2.29T     ├─   1 Year     +14.03% ▲   
  ├─   P/E Ratio     20.16      ├─   2 Years    +48.20% ▲   
  ├─   EPS (TTM)     $9.38      ├─   5 Years    +156.64% ▲  
  └─   Book Value    $29.98     └─   10 Years   +472.46% ▲  
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

### 📊 Fundamentals
- **Market Cap** - Total market capitalization
- **P/E Ratio** - Price-to-earnings ratio
- **EPS (TTM)** - Earnings Per Share (trailing 12 months)
- **Book Value** - Book value per share

### 🚀 Growth Performance
- **1-Year Growth** - Annual price performance
- **2-Year Growth** - Bi-annual price performance
- **5-Year Growth** - Half-decade price performance
- **10-Year Growth** - Decade-long investment returns
- **Color Coding**: Red ▼ for losses, Green ▲ for gains

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
