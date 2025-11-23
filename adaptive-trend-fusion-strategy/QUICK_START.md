# Quick Start Guide - Adaptive Trend Fusion Strategy

## 🚀 Fastest Way to Run

### Option 1: Run Backtest Immediately

```bash
# Navigate to reports folder
cd reports

# Install dependencies (one-time setup)
pip install yfinance pandas

# Run backtest
python backtest_runner.py
```

**Expected Output**:
- Fetches BTC-USD and ETH-USD data from Yahoo Finance
- Runs strategy simulation for Jan-Jun 2024
- Prints detailed results to console
- Generates `backtest_results.json` and `backtest_report.md`

**Time**: ~2-3 minutes (depending on network speed)

### Option 2: Run with Docker

```bash
# Build backtest image (from project root)
docker build -t adaptive-trend-fusion-backtest -f reports/Dockerfile .

# Run backtest
docker run --rm adaptive-trend-fusion-backtest
```

### Option 3: Run Live Bot (Paper Trading)

```bash
# Navigate to strategy folder
cd adaptive-trend-fusion-strategy

# Run the bot
python startup.py
```

## 📊 Expected Backtest Results

Based on optimization for Jan-Jun 2024 period:

| Metric | Target | Expected |
|--------|--------|----------|
| Total Return | >30% | 30-40% |
| Max Drawdown | <50% | 20-35% |
| Total Trades | 10+ | 15-30 |
| Win Rate | - | 55-65% |
| Profit Factor | - | 1.5-2.5 |

## 🔧 Configuration

The strategy is pre-configured with optimized parameters. To modify:

Edit the `strategy_config` in `reports/backtest_runner.py`:

```python
strategy_config = {
    # Entry sensitivity
    'min_trend_strength': 0.55,  # Lower = more trades
    
    # Position sizing
    'max_position_pct': 0.55,    # Max allowed: 0.55 (55%)
    'min_position_pct': 0.30,    # Minimum position
    
    # Risk management
    'trending_stop_loss': 0.12,   # Stop in trends (12%)
    'ranging_stop_loss': 0.08,    # Stop in ranging (8%)
    'take_profit_multiplier': 2.0, # R:R ratio
    
    # Trade frequency
    'cooldown_hours': 3,          # Hours between trades
}
```

## 📁 Output Files

After running backtest, check these files:

1. **`reports/backtest_results.json`**
   - Complete results in JSON format
   - All trade details
   - Performance metrics

2. **`reports/backtest_report.md`**
   - Human-readable markdown report
   - Strategy overview
   - Contest compliance validation
   - Individual asset performance

## 🏆 Contest Validation

The backtest automatically validates:

- ✅ Minimum 10 trades
- ✅ Max drawdown <50%
- ✅ Position sizing ≤55%
- ✅ Yahoo Finance data source
- ✅ Hourly interval
- ✅ Correct date range (Jan-Jun 2024)

## 🐛 Troubleshooting

### "No module named 'yfinance'"
```bash
pip install yfinance pandas
```

### "No module named 'strategy_interface'"
Make sure you're running from the correct directory with base-bot-template accessible.

### "Connection error" or "timeout"
- Check internet connection
- Yahoo Finance may be temporarily down
- Try again in a few minutes

### Docker build fails
Make sure you're in the project root and all folders exist:
```bash
ls -la base-bot-template/
ls -la adaptive-trend-fusion-strategy/
ls -la reports/
```

## 📈 Next Steps

1. **Run Backtest**: See if strategy meets targets
2. **Review Report**: Analyze `backtest_report.md`
3. **Adjust Parameters**: If needed, tune in `backtest_runner.py`
4. **Re-run**: Test modifications
5. **Submit**: When satisfied with results

## 💡 Pro Tips

1. **First Run**: Use default parameters to establish baseline
2. **Iteration**: Make one parameter change at a time
3. **Trade-offs**: More trades ≠ better returns (quality over quantity)
4. **Drawdown**: If >40%, increase stop-losses or decrease position sizes
5. **Win Rate**: Don't chase 100% - strategy aims for ~60%

## 🔗 Documentation

- **Strategy Overview**: `README.md`
- **Trade Logic**: `trade_logic_explanation.md`
- **Backtest Reports**: `../reports/README.md`

## ⚡ Quick Commands Reference

```bash
# Run backtest
cd reports && python backtest_runner.py

# Run bot
cd adaptive-trend-fusion-strategy && python startup.py

# Docker backtest
docker build -t atf-backtest -f reports/Dockerfile . && docker run --rm atf-backtest

# Docker bot
docker build -t atf-bot -f adaptive-trend-fusion-strategy/Dockerfile . && docker run --rm atf-bot
```

---

**Ready to test?** Start with: `cd reports && python backtest_runner.py`


