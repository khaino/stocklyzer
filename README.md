# Stocklyzer



A command line interface for stock analysis

* Free software: MIT License

## Features

* 📊 **Real-time stock data** from Yahoo Finance
* 🎨 **Beautiful terminal output** with rich tables and colors
* 💰 **Comprehensive stock information** including prices, market cap, P/E ratios
* 🚀 **Simple command-line interface** - just `slz ticker SYMBOL`
* ⚡ **Fast and lightweight** - no complex setup required

## Installation

Clone from GitHub and install locally:

```bash
git clone https://github.com/yourusername/stocklyzer.git
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

## Sample Output

### Apple Inc. (AAPL)
```
slz ticker AAPL
Fetching real stock data for AAPL...
Stock Information: AAPL (Apple Inc.)
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Metric        ┃ Value      ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ Symbol        │ AAPL       │
│ Current Price │ $213.88    │
│ Change        │ +0.12      │
│ Change %      │ +0.06%     │
│ Open          │ $214.70    │
│ High          │ $215.24    │
│ Low           │ $213.40    │
│ Volume        │ 40,219,700 │
│ Market Cap    │ $3.19T     │
│ P/E Ratio     │ 33.31      │
│ Sector        │ Technology │
└───────────────┴────────────┘
```

### Microsoft Corporation (MSFT)
```
slz ticker MSFT
Fetching real stock data for MSFT...
Stock Information: MSFT (Microsoft Corporation)
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Metric        ┃ Value      ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ Symbol        │ MSFT       │
│ Current Price │ $513.71    │
│ Change        │ +2.83      │
│ Change %      │ +0.55%     │
│ Open          │ $512.47    │
│ High          │ $518.29    │
│ Low           │ $510.36    │
│ Volume        │ 19,106,400 │
│ Market Cap    │ $3.82T     │
│ P/E Ratio     │ 39.67      │
│ Sector        │ Technology │
└───────────────┴────────────┘
```

### Alphabet Inc. (GOOGL)
```
slz ticker GOOGL
Fetching real stock data for GOOGL...
Stock Information: GOOGL (Alphabet Inc.)
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric        ┃ Value                  ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Symbol        │ GOOGL                  │
│ Current Price │ $193.18                │
│ Change        │ +1.01                  │
│ Change %      │ +0.53%                 │
│ Open          │ $191.98                │
│ High          │ $194.33                │
│ Low           │ $191.26                │
│ Volume        │ 39,743,800             │
│ Market Cap    │ $2.34T                 │
│ P/E Ratio     │ 20.57                  │
│ Sector        │ Communication Services │
└───────────────┴────────────────────────┘
```

## Available Information

For each stock ticker, Stocklyzer provides:

- **Current Price** - Latest trading price
- **Daily Change** - Price change and percentage change
- **Trading Data** - Open, High, Low prices
- **Volume** - Number of shares traded
- **Market Cap** - Total market capitalization
- **P/E Ratio** - Price-to-earnings ratio
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
