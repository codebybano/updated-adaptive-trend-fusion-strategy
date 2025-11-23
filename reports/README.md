# Backtest Reports

This folder contains the backtesting framework for the Adaptive Trend Fusion Strategy.

## Quick Start

### Run Backtest Locally

```bash
cd reports
python backtest_runner.py
```

### Run Backtest with Docker

```bash
# Build the Docker image
docker build -t adaptive-trend-fusion-backtest -f reports/Dockerfile .

# Run the backtest
docker run --rm adaptive-trend-fusion-backtest

# Run the backtest and also saving the results in local directory under /reports folder
docker run --rm -v "$(pwd)/reports:/app/reports" adaptive-trend-fusion-backtest
```

## Output Files

After running the backtest, you'll find:

- **`backtest_results.json`**: Detailed results in JSON format
- **`backtest_report.md`**: Human-readable markdown report

## Contest Requirements

The backtest validates:

- ✅ Minimum 10 trades over 6-month period
- ✅ Maximum drawdown <50%
- ✅ Target return >30%
- ✅ Position sizing ≤55%
- ✅ Yahoo Finance hourly data
- ✅ Date range: Jan 1 - Jun 30, 2024

## Data Source

All price data is fetched from **Yahoo Finance** using the `yfinance` library with hourly interval (`1h`).

## Strategy Tested

**Adaptive Trend Fusion Strategy**

- Uses Stochastic Oscillator, ADX, Williams %R
- Regime-adaptive position sizing
- Dynamic risk management
- Multi-timeframe confirmation

