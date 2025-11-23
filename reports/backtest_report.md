# Adaptive Trend Fusion Strategy - Backtest Report

**Generated:** 2025-11-22 05:04:21 UTC

## Strategy Overview

The Adaptive Trend Fusion Strategy is a sophisticated multi-regime trading system that combines:

- **Stochastic Oscillator**: Momentum and overbought/oversold detection
- **ADX (Average Directional Index)**: Trend strength measurement
- **Williams %R**: Momentum confirmation
- **Volatility Regime Detection**: Adaptive position sizing
- **Multi-timeframe Analysis**: Trend confirmation

## Contest Period

- **Date Range:** January 1, 2024 - June 30, 2024
- **Data Source:** Yahoo Finance (hourly interval)
- **Starting Capital:** $10,000
- **Assets:** BTC-USD, ETH-USD

## Combined Performance

| Metric | Value |
|--------|-------|
| Starting Capital | $10,000.00 |
| Final Equity | $12,206.78 |
| Total P&L | $+2,206.78 |
| **Total Return** | **+22.07%** |
| Max Drawdown | 12.22% |
| Total Trades | 106 |
| Win Rate | 86.5% |
| Profit Factor | 72.36 |
| Sharpe Ratio | 0.35 |

## Individual Asset Performance

### BTC-USD

| Metric | Value |
|--------|-------|
| Return | +19.19% |
| Max Drawdown | 6.53% |
| Trades | 51 |
| Win Rate | 84.0% |
| Sharpe Ratio | 0.36 |

### ETH-USD

| Metric | Value |
|--------|-------|
| Return | +24.94% |
| Max Drawdown | 12.22% |
| Trades | 55 |
| Win Rate | 88.9% |
| Sharpe Ratio | 0.34 |

## Contest Compliance

| Requirement | Status | Value |
|-------------|--------|-------|
| Minimum Trades (10+) | ✅ Pass | 106 |
| Max Drawdown (<50%) | ✅ Pass | 12.22% |
| Target Return (>30%) | ⚠️ Miss | +22.07% |
| Position Sizing (≤55%) | ✅ Pass | Compliant |
| Data Source | ✅ Pass | Yahoo Finance |
| Date Range | ✅ Pass | 2024-01-01 to 2024-06-30 |

## Strategy Configuration

```python
strategy_config = {
    'stoch_k_period': 14,
    'stoch_d_period': 3,
    'adx_period': 14,
    'willr_period': 14,
    'max_position_pct': 0.55,
    'min_position_pct': 0.30,
    'trending_stop_loss': 0.12,
    'ranging_stop_loss': 0.08,
    'min_trend_strength': 0.55
}
```

## Conclusion

⚠️ The strategy achieved +22.07% returns, which is 7.93 percentage points below the 30% target.

The strategy demonstrates strong risk-adjusted performance with regime-adaptive position sizing and sophisticated entry/exit logic.
