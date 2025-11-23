# Adaptive Trend Fusion Strategy

A sophisticated multi-regime trading strategy that adapts to market conditions for optimal cryptocurrency trading performance.

## 🎯 Strategy Overview

The Adaptive Trend Fusion Strategy combines multiple technical indicators with regime detection to achieve superior risk-adjusted returns. Unlike traditional strategies that use the same approach in all market conditions, this strategy **adapts** its behavior based on whether the market is trending, ranging, or experiencing high volatility.

### Core Innovation

**Regime-Adaptive Trading**: The strategy automatically detects market regimes and adjusts:
- Position sizing (aggressive in strong trends, conservative in ranging markets)
- Stop-loss distances (wider in trends, tighter in uncertainty)
- Entry thresholds (higher confidence required in high volatility)
- Exit strategies (trailing stops in trends, quick exits in reversals)

## 📊 Technical Indicators

### Primary Indicators

1. **Stochastic Oscillator (%K, %D)**
   - Identifies overbought/oversold conditions
   - Provides precise entry timing
   - Detects momentum shifts

2. **ADX (Average Directional Index)**
   - Measures trend strength (0-100 scale)
   - Filters weak trends vs strong trends
   - Combines with +DI/-DI for directional bias

3. **Williams %R**
   - Momentum confirmation indicator
   - Oversold/overbought detection
   - Validates Stochastic signals

4. **Multi-Timeframe Moving Averages**
   - Fast MA (10-period): Short-term trend
   - Medium MA (20-period): Intermediate trend
   - Slow MA (50-period): Long-term trend
   - MA alignment confirms trend direction

### Regime Detection System

The strategy classifies markets into four regimes:

1. **Trending Up** 🟢
   - Strong uptrend confirmed by ADX >25
   - Price above all MAs
   - +DI > -DI
   - Action: Maximum position sizing, wider stops

2. **Trending Down** 🔴
   - Strong downtrend confirmed by ADX >25
   - Price below all MAs
   - -DI > +DI
   - Action: Stay out, await reversal

3. **Ranging** 🟡
   - Weak trend (ADX <25)
   - No clear MA alignment
   - Action: Conservative position sizing, tighter stops

4. **High Volatility** 🟠
   - Hourly volatility >3.5%
   - Unpredictable price action
   - Action: Minimal/no exposure

## 💼 Position Sizing

Dynamic position sizing based on:
- **Regime strength**: 25-55% of portfolio
- **Confidence level**: Higher conviction = larger size
- **Available capital**: Never overleverage
- **Contest compliance**: Maximum 55% per trade

Example:
- Strong uptrend + high confidence → 50-55% position
- Ranging market + moderate confidence → 30-35% position
- High volatility → 15-25% position (or stay out)

## 🛡️ Risk Management

### Stop-Loss Strategy

**Adaptive stops based on regime:**
- Trending markets: 12% stop-loss (give room to breathe)
- Ranging markets: 8% stop-loss (tighter control)

### Take-Profit Strategy

**Dynamic targets:**
- Target = Stop-Loss × 2.0 multiplier
- Example: 12% stop → 24% target
- Trailing stop activates at 10% profit
- Trails 6% below peak

### Exit Conditions

1. **Hard stop-loss triggered**
2. **Take-profit target reached**
3. **Trailing stop triggered** (in profit)
4. **Regime change** (e.g., trending → high volatility)
5. **Bearish reversal signals** (with profit secured)
6. **Multiple overbought indicators** (Stochastic + Williams %R)

## 📈 Expected Performance

### Target Metrics (Jan-Jun 2024)

- **Total Return**: >30%
- **Max Drawdown**: <50%
- **Win Rate**: 55-65%
- **Profit Factor**: >1.5
- **Sharpe Ratio**: >1.0
- **Total Trades**: 15-30

### Strengths

✅ Adapts to different market conditions
✅ Strong trend capture with room to run
✅ Disciplined risk management
✅ Multi-indicator confirmation reduces false signals
✅ Sophisticated regime detection

### Considerations

⚠️ Requires sufficient lookback data (50+ periods)
⚠️ May underperform in choppy sideways markets
⚠️ Cooldown periods may miss some opportunities

## 🚀 Usage

### Local Development

```bash
# Install dependencies
pip install -r ../base-bot-template/requirements.txt

# Run the strategy
python startup.py
```

### Docker Deployment

```bash
# Build the image
docker build -t adaptive-trend-fusion -f Dockerfile .

# Run the bot
docker run --rm \
  -e BOT_EXCHANGE=paper \
  -e BOT_STRATEGY=adaptive_trend_fusion \
  -e BOT_SYMBOL=BTC-USD \
  -e BOT_STARTING_CASH=10000 \
  adaptive-trend-fusion
```

### Configuration

Key parameters in strategy config:

```python
config = {
    # Indicator periods
    'stoch_k_period': 14,
    'stoch_d_period': 3,
    'adx_period': 14,
    'willr_period': 14,
    
    # Position sizing
    'max_position_pct': 0.55,  # Max 55% per contest rules
    'min_position_pct': 0.30,
    
    # Risk management
    'trending_stop_loss': 0.12,
    'ranging_stop_loss': 0.08,
    'take_profit_multiplier': 2.0,
    
    # Entry criteria
    'min_trend_strength': 0.55,  # 55% confidence threshold
    'cooldown_hours': 3
}
```

## 🏆 Contest Compliance

This strategy is designed for the trading contest with strict requirements:

- ✅ **Data Source**: Yahoo Finance only (yfinance library)
- ✅ **Interval**: Hourly data (`1h`)
- ✅ **Date Range**: 2024-01-01 to 2024-06-30
- ✅ **Starting Capital**: $10,000
- ✅ **Position Sizing**: Maximum 55% exposure
- ✅ **Drawdown Limit**: <50%
- ✅ **Minimum Trades**: 10+ over period
- ✅ **Platform**: Inherits from BaseStrategy

## 📝 Trade Logic Example

### Entry Example

```
Market Conditions:
- Price: $65,000
- Stochastic %K: 28 (oversold)
- ADX: 32 (strong trend)
- +DI: 35, -DI: 15 (bullish)
- Price > all MAs (uptrend confirmation)
- Regime: "trending_up"

Decision: BUY
- Position size: 50% of portfolio ($5,000)
- Entry: $65,000
- Stop-loss: $57,200 (12% below)
- Target: $80,600 (24% above)
```

### Exit Example

```
Market Conditions:
- Entry price: $65,000
- Current price: $71,500 (+10%)
- Highest since entry: $73,000
- Current drop from peak: 2%

Trailing stop activated (10% profit threshold reached)
Trailing distance: 6%

If price drops to $68,620 (6% from peak):
Decision: SELL - "Trailing stop triggered"
Result: Profit secured at ~5.5%
```

## 🔬 Backtesting

Run comprehensive backtests:

```bash
cd ../reports
python backtest_runner.py
```

This will:
1. Fetch BTC-USD and ETH-USD hourly data from Yahoo Finance
2. Run strategy simulation for Jan-Jun 2024
3. Generate detailed performance metrics
4. Create `backtest_results.json` and `backtest_report.md`
5. Validate contest compliance

## 🧠 Strategy Philosophy

> "The market has different personalities. A winning strategy must recognize when the market is trending powerfully versus when it's confused and directionless. By adapting our approach to the current regime, we maximize gains in favorable conditions while protecting capital in uncertain times."

### Key Principles

1. **Regime Recognition**: Markets alternate between trending and ranging - trade accordingly
2. **Confluence of Signals**: Multiple indicators must agree before entry
3. **Let Winners Run**: Wider stops in trends allow for big gains
4. **Cut Losses Quickly**: Tighter stops in uncertainty prevent large drawdowns
5. **Position Sizing Matters**: Risk more in high-probability setups

## 📚 Further Reading

- **Stochastic Oscillator**: Lane, George (1984)
- **ADX**: Wilder, J. Welles (1978) - "New Concepts in Technical Trading Systems"
- **Williams %R**: Williams, Larry (1979)
- **Regime Detection**: See academic papers on market regime classification

## 🤝 Contributing

This strategy is designed for contest submission. For improvements or variations:

1. Test modifications thoroughly with backtesting
2. Ensure contest compliance is maintained
3. Document parameter changes and rationale
4. Validate performance against benchmarks

## ⚖️ License

This strategy is part of the crypto-strategy-python repository. See main README for license details.

---

**Strategy Author**: Adaptive Trend Fusion Team  
**Version**: 1.0  
**Last Updated**: 2024  
**Contest Target**: >30% returns with <50% drawdown


