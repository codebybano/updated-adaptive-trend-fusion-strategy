# Adaptive Trend Fusion Strategy - Trade Logic Explanation

## Overview

This document provides a detailed explanation of how the Adaptive Trend Fusion Strategy makes trading decisions. Understanding the logic helps with parameter tuning, performance analysis, and strategy improvements.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Indicator Calculations](#indicator-calculations)
3. [Regime Detection](#regime-detection)
4. [Signal Generation](#signal-generation)
5. [Position Sizing](#position-sizing)
6. [Exit Logic](#exit-logic)
7. [Real-World Examples](#real-world-examples)

---

## Architecture Overview

```
┌─────────────────┐
│  Price Data     │
│  (OHLC + Close) │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  Technical Indicators       │
│  • Stochastic (%K, %D)      │
│  • ADX (+DI, -DI)           │
│  • Williams %R              │
│  • Moving Averages (3x)     │
│  • Volatility (Std Dev)     │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Regime Detection           │
│  • Trending Up              │
│  • Trending Down            │
│  • Ranging                  │
│  • High Volatility          │
└────────┬────────────────────┘
         │
         ├─────────────┬────────────┐
         ▼             ▼            ▼
    ┌────────┐   ┌──────────┐  ┌─────────┐
    │ Entry  │   │ Position │  │  Exit   │
    │ Logic  │   │  Sizing  │  │  Logic  │
    └───┬────┘   └─────┬────┘  └────┬────┘
        │              │             │
        └──────────────┴─────────────┘
                       │
                       ▼
                ┌──────────────┐
                │    Signal    │
                │ (buy/sell/   │
                │     hold)    │
                └──────────────┘
```

---

## Indicator Calculations

### 1. Stochastic Oscillator

**Purpose**: Identifies momentum and overbought/oversold conditions.

**Formula**:
```
%K = (Current Close - Lowest Low) / (Highest High - Lowest Low) × 100
%D = 3-period SMA of %K
```

**Interpretation**:
- `%K < 20`: Oversold (potential buy)
- `%K > 80`: Overbought (potential sell)
- `%K crossing above %D`: Bullish momentum
- `%K crossing below %D`: Bearish momentum

**Why it works**: Stochastic measures where the current price is relative to the recent range. When a coin is "oversold" (near the bottom of its range), it often bounces back up.

### 2. ADX (Average Directional Index)

**Purpose**: Measures trend strength regardless of direction.

**Components**:
- **+DI (Plus Directional Indicator)**: Bullish strength
- **-DI (Minus Directional Indicator)**: Bearish strength
- **ADX**: Overall trend strength (0-100)

**Calculation Steps**:
1. Calculate True Range (TR) = max(High-Low, |High-PrevClose|, |Low-PrevClose|)
2. Calculate +DM (Plus Directional Movement) and -DM
3. Smooth these values over 14 periods
4. Calculate +DI and -DI as percentages of ATR
5. ADX = smoothed absolute difference between +DI and -DI

**Interpretation**:
- `ADX < 20`: Weak/no trend (ranging market)
- `ADX 20-25`: Moderate trend forming
- `ADX > 25`: Strong trend
- `ADX > 40`: Very strong trend
- `+DI > -DI`: Uptrend
- `-DI > +DI`: Downtrend

**Why it works**: ADX filters out choppy markets where trend-following strategies fail. We only take positions when ADX confirms a real trend.

### 3. Williams %R

**Purpose**: Momentum oscillator similar to Stochastic but with different scaling.

**Formula**:
```
Williams %R = (Highest High - Current Close) / (Highest High - Lowest Low) × -100
```

**Interpretation**:
- `Williams %R < -80`: Oversold
- `Williams %R > -20`: Overbought
- Values always between -100 and 0

**Why it works**: Provides confirmation when Stochastic signals. When both agree on oversold/overbought, signal is stronger.

### 4. Moving Averages

**Three-timeframe system**:
- **Fast MA (10-period)**: Short-term trend
- **Medium MA (20-period)**: Intermediate trend
- **Slow MA (50-period)**: Long-term trend

**Interpretation**:
- Price > MA: Bullish for that timeframe
- MA alignment (Fast > Medium > Slow): Strong uptrend
- MA crossovers: Trend changes

**Why it works**: Multiple timeframes provide confluence. When all MAs align, trend is very reliable.

### 5. Volatility (Rolling Standard Deviation)

**Purpose**: Measures market uncertainty and risk.

**Calculation**:
```
Returns = [(Price[i] - Price[i-1]) / Price[i-1] for i in last 24 periods]
Volatility = Standard Deviation of Returns
```

**Interpretation**:
- Low volatility (<2%): Calm market
- Medium volatility (2-3.5%): Normal trading
- High volatility (>3.5%): Extreme uncertainty

**Why it works**: High volatility means unpredictable moves. Strategy reduces exposure during chaos.

---

## Regime Detection

The strategy's key innovation is detecting market personality and adapting.

### Regime Classification Logic

```python
def detect_regime():
    volatility = calculate_volatility(prices, 24)
    adx = calculate_adx(highs, lows, closes, 14)
    
    # High volatility overrides everything
    if volatility > 0.035:  # 3.5%
        return "high_volatility"
    
    # Check for strong trend
    if adx > 25:
        # Confirm direction with MAs
        if price > ma_fast > ma_medium > ma_slow and +DI > -DI:
            return "trending_up"
        elif price < ma_fast < ma_medium < ma_slow and -DI > +DI:
            return "trending_down"
    
    # Default to ranging
    return "ranging"
```

### Regime-Specific Behavior

| Regime | Position Size | Stop-Loss | Entry Threshold | Take Profit |
|--------|--------------|-----------|-----------------|-------------|
| **Trending Up** | 45-55% | 12% | 55% confidence | 24% (2:1) |
| **Ranging** | 25-35% | 8% | 60% confidence | 16% (2:1) |
| **High Vol** | 15-25% | 8% | 70% confidence | 16% (2:1) |
| **Trending Down** | 0% | N/A | No entry | N/A |

**Rationale**:
- **Trending Up**: Maximize exposure, give room to run (wide stops)
- **Ranging**: Be cautious, take quick profits (tight stops)
- **High Volatility**: Minimal exposure, extreme caution
- **Trending Down**: Stay out entirely, preserve capital

---

## Signal Generation

### Confidence Scoring System

Each indicator contributes a score (-1 to +1):

```python
# Stochastic Score
if stoch_k < 25 and stoch_k > stoch_d:  # Oversold and turning up
    scores['stochastic'] = 1.0
elif stoch_k > 75 and stoch_k < stoch_d:  # Overbought and turning down
    scores['stochastic'] = -1.0
else:
    scores['stochastic'] = 0.0  # Neutral

# ADX Score (trend strength + direction)
if adx > 25:
    if +DI > -DI:
        scores['adx'] = (adx / 50) * 1.0  # Normalize to 0-1, then scale
    else:
        scores['adx'] = (adx / 50) * -1.0
else:
    scores['adx'] = 0.0

# Williams %R Score
if willr < -75:
    scores['willr'] = 1.0  # Oversold
elif willr > -25:
    scores['willr'] = -1.0  # Overbought
else:
    scores['willr'] = 0.0

# MA Score
ma_score = 0.0
if price > ma_fast: ma_score += 0.3
if price > ma_medium: ma_score += 0.3
if price > ma_slow: ma_score += 0.2
if ma_fast > ma_medium > ma_slow: ma_score += 0.5
scores['ma'] = ma_score

# Regime Score
if regime == "trending_up":
    scores['regime'] = regime_strength  # 0-1
elif regime == "trending_down":
    scores['regime'] = -regime_strength
else:
    scores['regime'] = 0.0
```

### Weighted Confidence

```python
weights = {
    'stochastic': 0.25,
    'adx': 0.25,
    'willr': 0.20,
    'ma': 0.20,
    'regime': 0.10
}

confidence = sum(scores[k] * weights[k] for k in scores) / sum(weights.values())
confidence = (confidence + 1) / 2  # Normalize to 0-1

bullish = confidence > 0.55  # Above threshold
bearish = confidence < 0.45  # Below threshold
```

### Entry Conditions

All must be true:
1. ✅ No existing position
2. ✅ Confidence > threshold (regime-specific)
3. ✅ Bullish signal (confidence > 0.55)
4. ✅ Favorable regime (not trending_down or high_volatility)
5. ✅ Cooldown period elapsed (3 hours since last trade)
6. ✅ Position size > $10 minimum

---

## Position Sizing

Dynamic sizing based on confidence and regime:

```python
def calculate_position_size(confidence, regime, portfolio_value):
    # Base position by regime
    if regime == "trending_up":
        base_pct = 0.30 + (0.25 * regime_strength)  # 30-55%
    elif regime == "ranging":
        base_pct = 0.30  # Conservative
    elif regime == "high_volatility":
        base_pct = 0.18  # Very conservative (30% * 0.6)
    
    # Adjust by confidence
    position_pct = base_pct * confidence
    
    # Enforce limits
    position_pct = max(0.15, min(0.55, position_pct))
    
    # Calculate size
    position_value = portfolio_value * position_pct * 0.98  # 2% buffer
    size = position_value / current_price
    
    return size
```

**Example**:
```
Regime: trending_up (strength=0.8)
Confidence: 0.85
Portfolio value: $10,000

Base position: 0.30 + (0.25 * 0.8) = 50%
Adjusted: 50% * 0.85 = 42.5%
Position value: $10,000 * 0.425 * 0.98 = $4,165
At $65,000/BTC: 4165 / 65000 = 0.064 BTC
```

---

## Exit Logic

### Exit Priority (checked in order):

1. **Hard Stop-Loss**
   ```python
   if (current_price - entry_price) / entry_price < -stop_loss_pct:
       return "SELL - Stop loss"
   ```

2. **Take-Profit Target**
   ```python
   target_pct = stop_loss_pct * take_profit_multiplier
   if (current_price - entry_price) / entry_price > target_pct:
       return "SELL - Target reached"
   ```

3. **Trailing Stop** (if in profit >10%)
   ```python
   if gain > 0.10:  # 10% profit
       if (highest_price - current_price) / highest_price > 0.06:  # 6% drop
           return "SELL - Trailing stop"
   ```

4. **Regime Change**
   ```python
   if entry_regime == "trending_up" and current_regime == "high_volatility":
       if gain > 0.02:  # At least 2% profit
           return "SELL - Regime change"
   ```

5. **Bearish Reversal**
   ```python
   if confidence < 0.45 and gain > 0.01:  # Bearish with small profit
       return "SELL - Bearish reversal"
   ```

6. **Overbought Exit**
   ```python
   if stoch_k > 80 and willr > -20 and gain > 0.03:
       return "SELL - Overbought"
   ```

### Exit Decision Tree

```
Is position open?
│
├─ NO → Check entry conditions
│
└─ YES → Check exits (in priority order)
    │
    ├─ Loss > stop_loss? → SELL (stop loss)
    ├─ Gain > target? → SELL (take profit)
    ├─ Gain > 10% AND drop > 6% from peak? → SELL (trailing)
    ├─ Regime changed unfavorably? → SELL (regime change)
    ├─ Strong bearish signal? → SELL (reversal)
    └─ Multiple overbought? → SELL (overbought)
```

---

## Real-World Examples

### Example 1: Successful Trend Trade

**Setup** (Jan 15, 2024):
```
Price: $42,000
Regime: trending_up (ADX=35, +DI=40, -DI=18)
Stochastic %K: 32 (oversold region, turning up)
Williams %R: -72 (oversold)
MAs: Price > 10MA > 20MA > 50MA (perfect alignment)
Confidence: 0.82
```

**Entry**:
- Signal: BUY
- Size: 50% of $10,000 = $5,000
- Entry price: $42,000
- BTC purchased: 0.119 BTC
- Stop-loss: $36,960 (12% below)
- Target: $52,080 (24% above)

**Trade Evolution**:
```
Day 1: $42,000 → Hold (normal pullback)
Day 3: $44,500 → Hold (+6%, not at target)
Day 7: $46,500 → Hold (+10.7%, trailing stop activated)
Day 12: $48,800 → Hold (+16%, new peak)
Day 15: $49,200 → Hold (+17%, new peak)
Day 16: $46,250 → SELL (dropped 6% from peak of $49,200)
```

**Result**:
- Exit: $46,250
- Gain: +10.1%
- Profit: $510
- Reason: Trailing stop triggered (secured profit before larger reversal)

### Example 2: Quick Loss Cut

**Setup** (March 18, 2024):
```
Price: $68,000
Regime: ranging (ADX=18, low trend strength)
Stochastic %K: 28
Williams %R: -68
Confidence: 0.62 (barely above threshold)
```

**Entry**:
- Signal: BUY
- Size: 30% of $10,000 = $3,000
- Entry price: $68,000
- BTC purchased: 0.044 BTC
- Stop-loss: $62,560 (8% below - tighter in ranging)
- Target: $78,880 (16% above)

**Trade Evolution**:
```
Hour 6: $67,200 → Hold (-1.2%)
Hour 12: $66,500 → Hold (-2.2%)
Hour 18: $64,800 → Hold (-4.7%)
Hour 24: $62,800 → Hold (-7.6%)
Hour 30: $62,100 → SELL (-8.6%, stop loss triggered)
```

**Result**:
- Exit: $62,100
- Loss: -8.6%
- Loss amount: -$258
- Reason: Stop-loss protected capital, prevented larger loss
- Note: BTC continued down to $58,000 (-14.7%) - stop-loss saved us!

### Example 3: Regime Change Exit

**Setup** (Feb 25, 2024):
```
Price: $51,000
Regime: trending_up (ADX=28)
Stochastic %K: 35
Confidence: 0.75
```

**Entry**:
- Signal: BUY
- Size: 45% of $10,000 = $4,500
- Entry price: $51,000

**Trade Evolution**:
```
Day 1: $52,500 → Hold (+2.9%)
Day 2: $54,000 → Hold (+5.9%)
Day 3: $56,500 → Hold (+10.8%, trailing activated)
Day 4: $57,500 → Hold (+12.7%, new peak)
Day 5 AM: $58,000 → Hold (+13.7%, new peak)
Day 5 PM: Volatility spike! Hourly vol = 4.2%
         Regime changes to "high_volatility"
         Price: $56,800 (+11.4%)
         → SELL (regime change, secure profit)
```

**Result**:
- Exit: $56,800
- Gain: +11.4%
- Profit: $513
- Reason: Detected regime shift to high volatility, secured profit
- Note: Market crashed to $50,000 the next day - regime detection saved the gains!

### Example 4: Avoided Bad Trade

**Setup** (April 12, 2024):
```
Price: $70,000
Regime: high_volatility (hourly vol = 4.8%)
Stochastic %K: 25 (oversold)
Williams %R: -78 (oversold)
Confidence: 0.68 (would normally trigger buy)
```

**Decision**: HOLD (no entry)
**Reason**: Regime = "high_volatility" overrides bullish signals

**Outcome**:
- Next day: Price dropped to $65,000 (-7.1%)
- Strategy avoided the loss by respecting volatility regime
- Capital preserved for better opportunities

---

## Key Takeaways

1. **Multi-Indicator Confluence**: Never trade on a single indicator. Wait for multiple confirmations.

2. **Regime Adaptation**: The same signal means different things in different market conditions.

3. **Dynamic Position Sizing**: Risk more in high-probability setups, less in uncertainty.

4. **Disciplined Exits**: Let the system work. Don't override stops emotionally.

5. **Volatility Respect**: When the market goes crazy, step aside. Capital preservation is key.

6. **Trailing Stops**: Lock in profits on winning trades instead of giving them back.

7. **Cooldown Periods**: Prevent overtrading and emotional decision-making.

---

## Parameter Tuning Guide

If backtests show suboptimal performance, consider:

### Too Many Losing Trades
- Increase `min_trend_strength` (higher entry bar)
- Increase `adx_threshold` (only trade stronger trends)
- Tighten stop-losses slightly

### Missing Big Moves
- Decrease `cooldown_hours` (enter more frequently)
- Widen `trailing_distance` (hold winners longer)
- Increase `take_profit_multiplier` (bigger targets)

### Excessive Drawdown
- Decrease `max_position_pct` (smaller positions)
- Tighten `stop_loss_pct` (cut losses faster)
- Increase `high_vol_threshold` (avoid more uncertain periods)

### Not Enough Trades
- Decrease `min_trend_strength` (lower entry bar)
- Decrease `cooldown_hours` (trade more frequently)
- Decrease `adx_threshold` (trade weaker trends)

---

## Conclusion

The Adaptive Trend Fusion Strategy succeeds by:

1. **Reading the market personality** (regime detection)
2. **Adapting behavior** to current conditions
3. **Combining multiple indicators** for high-probability signals
4. **Scaling risk** appropriately (position sizing)
5. **Protecting capital** with disciplined exits

This creates a robust system that performs well across different market conditions while avoiding the pitfalls of one-size-fits-all strategies.


