#!/usr/bin/env python3
"""Adaptive Trend Fusion Strategy - Multi-Regime Trading System.

This strategy combines volatility regime detection with adaptive position sizing
and multiple momentum indicators to capture strong trends while protecting capital
during uncertain market conditions.

Core Components:
1. Stochastic Oscillator - momentum and overbought/oversold conditions
2. ADX (Average Directional Index) - trend strength measurement
3. Williams %R - momentum confirmation
4. Volatility Regime Detection - adapt strategy to market conditions
5. Multi-timeframe price action - trend confirmation
6. Dynamic position sizing - scale in/out based on conviction
"""

from __future__ import annotations

import sys
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Deque
from collections import deque
from statistics import mean, stdev
import logging

# Handle both local development and Docker container paths
base_path = os.path.join(os.path.dirname(__file__), '..', 'base-bot-template')
if not os.path.exists(base_path):
    base_path = '/app/base'

sys.path.insert(0, base_path)

from strategy_interface import BaseStrategy, Signal, Portfolio, register_strategy
from exchange_interface import MarketSnapshot


class AdaptiveTrendFusionStrategy(BaseStrategy):
    """Advanced adaptive strategy that adjusts to market regimes for optimal returns.
    
    This strategy aims to achieve >30% returns by:
    - Detecting and adapting to volatility regimes (trending vs ranging)
    - Using Stochastic Oscillator for precise entry/exit timing
    - Employing ADX to filter for strong trends
    - Confirming with Williams %R momentum
    - Scaling position size based on trend strength and regime
    - Implementing regime-specific risk management
    """
    
    def __init__(self, config: Dict[str, Any], exchange):
        super().__init__(config=config, exchange=exchange)
        
        # Stochastic Oscillator parameters
        self.stoch_k_period = int(config.get("stoch_k_period", 14))
        self.stoch_d_period = int(config.get("stoch_d_period", 3))
        self.stoch_oversold = float(config.get("stoch_oversold", 20))
        self.stoch_overbought = float(config.get("stoch_overbought", 80))
        
        # ADX parameters
        self.adx_period = int(config.get("adx_period", 14))
        self.adx_threshold = float(config.get("adx_threshold", 24))  # Trend strength threshold
        
        # Williams %R parameters
        self.willr_period = int(config.get("willr_period", 14))
        self.willr_oversold = float(config.get("willr_oversold", -80))
        self.willr_overbought = float(config.get("willr_overbought", -20))
        
        # Moving averages for trend
        self.ma_fast = int(config.get("ma_fast", 9))
        self.ma_medium = int(config.get("ma_medium", 20))
        self.ma_slow = int(config.get("ma_slow", 50))
        
        # Volatility regime detection
        self.volatility_lookback = int(config.get("volatility_lookback", 24))  # 24 hours
        self.high_vol_threshold = float(config.get("high_vol_threshold", 0.03))  # 3% hourly volatility
        
        # Position sizing (max 55% per contest rules)
        self.max_position_pct = min(float(config.get("max_position_pct", 0.50)), 0.55)
        self.min_position_pct = float(config.get("min_position_pct", 0.28))
        
        # Risk management - adaptive by regime
        self.trending_stop_loss = float(config.get("trending_stop_loss", 0.11))  # 11% in trends
        self.ranging_stop_loss = float(config.get("ranging_stop_loss", 0.07))  # 7% in ranging
        self.take_profit_multiplier = float(config.get("take_profit_multiplier", 3.0))  # 3.0x risk
        self.trailing_activation = float(config.get("trailing_activation", 0.12))  # Activate at 12% profit
        self.trailing_distance = float(config.get("trailing_distance", 0.055))  # 5.5% trailing
        
        # Trade management
        self.min_trend_strength = float(config.get("min_trend_strength", 0.50))  # 50% confidence
        self.cooldown_hours = int(config.get("cooldown_hours", 0))
        
        # State tracking
        self.positions: Deque[Dict[str, Any]] = deque(maxlen=10)
        self.last_trade_time: Optional[datetime] = None
        self.highest_price_since_entry: Optional[float] = None
        self.price_history: Deque[float] = deque(maxlen=300)
        self.high_history: Deque[float] = deque(maxlen=300)
        self.low_history: Deque[float] = deque(maxlen=300)
        self.current_regime: str = "unknown"  # "trending_up", "trending_down", "ranging", "high_volatility"
        
        # Logging
        self._logger = logging.getLogger("strategy.adaptive_trend_fusion")
        self._log("INIT", f"Adaptive Trend Fusion Strategy initialized with max_position={self.max_position_pct*100}%")
    
    def _log(self, kind: str, msg: str) -> None:
        """Safe logging."""
        try:
            self._logger.info(f"[ATF/{kind}] {msg}")
        except Exception:
            pass
    
    # ==================== TECHNICAL INDICATORS ====================
    
    def _calculate_stochastic(self, highs: list, lows: list, closes: list, k_period: int = 14, d_period: int = 3) -> tuple[float, float]:
        """Calculate Stochastic Oscillator %K and %D."""
        if len(closes) < k_period or len(highs) < k_period or len(lows) < k_period:
            return 50.0, 50.0  # Neutral
        
        # Calculate %K
        recent_highs = highs[-k_period:]
        recent_lows = lows[-k_period:]
        current_close = closes[-1]
        
        highest_high = max(recent_highs)
        lowest_low = min(recent_lows)
        
        if highest_high == lowest_low:
            k_value = 50.0
        else:
            k_value = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
        
        # Calculate %D (moving average of %K)
        # For simplicity, we'll calculate %K for the last d_period and average
        k_values = []
        for i in range(max(k_period, len(closes) - d_period), len(closes)):
            if i >= k_period:
                period_highs = highs[i-k_period:i]
                period_lows = lows[i-k_period:i]
                period_close = closes[i-1] if i > 0 else closes[0]
                
                h = max(period_highs) if period_highs else current_close
                l = min(period_lows) if period_lows else current_close
                
                if h == l:
                    k_values.append(50.0)
                else:
                    k_values.append(((period_close - l) / (h - l)) * 100)
        
        k_values.append(k_value)
        d_value = mean(k_values[-d_period:]) if len(k_values) >= d_period else k_value
        
        return k_value, d_value
    
    def _calculate_adx(self, highs: list, lows: list, closes: list, period: int = 14) -> tuple[float, float, float]:
        """Calculate ADX (Average Directional Index), +DI, -DI."""
        if len(closes) < period + 1:
            return 0.0, 0.0, 0.0
        
        # Calculate True Range and Directional Movement
        tr_list = []
        plus_dm_list = []
        minus_dm_list = []
        
        for i in range(1, len(closes)):
            high = highs[i]
            low = lows[i]
            prev_high = highs[i-1]
            prev_low = lows[i-1]
            prev_close = closes[i-1]
            
            # True Range
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            tr_list.append(tr)
            
            # Directional Movement
            plus_dm = max(high - prev_high, 0) if (high - prev_high) > (prev_low - low) else 0
            minus_dm = max(prev_low - low, 0) if (prev_low - low) > (high - prev_high) else 0
            
            plus_dm_list.append(plus_dm)
            minus_dm_list.append(minus_dm)
        
        if len(tr_list) < period:
            return 0.0, 0.0, 0.0
        
        # Calculate smoothed TR, +DM, -DM
        atr = mean(tr_list[-period:])
        plus_dm_smooth = mean(plus_dm_list[-period:])
        minus_dm_smooth = mean(minus_dm_list[-period:])
        
        # Calculate +DI and -DI
        plus_di = (plus_dm_smooth / atr * 100) if atr > 0 else 0
        minus_di = (minus_dm_smooth / atr * 100) if atr > 0 else 0
        
        # Calculate DX and ADX
        di_sum = plus_di + minus_di
        if di_sum == 0:
            dx = 0
        else:
            dx = abs(plus_di - minus_di) / di_sum * 100
        
        # ADX is smoothed DX (simplified - just using recent average)
        adx = dx  # In production, would use exponential smoothing
        
        return adx, plus_di, minus_di
    
    def _calculate_williams_r(self, highs: list, lows: list, closes: list, period: int = 14) -> float:
        """Calculate Williams %R indicator."""
        if len(closes) < period:
            return -50.0  # Neutral
        
        highest_high = max(highs[-period:])
        lowest_low = min(lows[-period:])
        current_close = closes[-1]
        
        if highest_high == lowest_low:
            return -50.0
        
        willr = ((highest_high - current_close) / (highest_high - lowest_low)) * -100
        return willr
    
    def _calculate_ma(self, prices: list, period: int) -> Optional[float]:
        """Calculate Simple Moving Average."""
        if len(prices) < period:
            return None
        return mean(prices[-period:])
    
    def _calculate_volatility(self, prices: list, period: int = 24) -> float:
        """Calculate historical volatility (standard deviation of returns)."""
        if len(prices) < period + 1:
            return 0.0
        
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(-period, 0)]
        return stdev(returns) if len(returns) > 1 else 0.0
    
    def _detect_regime(self, prices: list, highs: list, lows: list, closes: list) -> tuple[str, float]:
        """Detect market regime: trending_up, trending_down, ranging, high_volatility."""
        if len(prices) < self.ma_slow:
            return "unknown", 0.5
        
        # Calculate indicators for regime detection
        ma_fast = self._calculate_ma(prices, self.ma_fast)
        ma_medium = self._calculate_ma(prices, self.ma_medium)
        ma_slow = self._calculate_ma(prices, self.ma_slow)
        volatility = self._calculate_volatility(prices, self.volatility_lookback)
        adx, plus_di, minus_di = self._calculate_adx(highs, lows, closes, self.adx_period)
        
        current_price = prices[-1]
        
        # High volatility regime
        if volatility > self.high_vol_threshold:
            return "high_volatility", 0.3
        
        # Check trend strength with ADX
        if adx > self.adx_threshold and ma_fast and ma_medium and ma_slow:
            # Strong trend exists
            if current_price > ma_fast > ma_medium > ma_slow and plus_di > minus_di:
                # Strong uptrend
                trend_strength = min(1.0, adx / 50)  # Normalize ADX
                return "trending_up", trend_strength
            elif current_price < ma_fast < ma_medium < ma_slow and minus_di > plus_di:
                # Strong downtrend
                trend_strength = min(1.0, adx / 50)
                return "trending_down", trend_strength
        
        # Ranging market (weak trend)
        return "ranging", 0.4
    
    # ==================== SIGNAL GENERATION ====================
    
    def _analyze_indicators(self, prices: list, highs: list, lows: list, closes: list) -> Dict[str, Any]:
        """Analyze indicators with TREND-FOLLOWING focus for maximum returns."""
        
        current_price = prices[-1]
        
        # Calculate MAs - PRIMARY signal source
        ma_fast = self._calculate_ma(prices, self.ma_fast)
        ma_medium = self._calculate_ma(prices, self.ma_medium)
        ma_slow = self._calculate_ma(prices, self.ma_slow)
        
        # Calculate rate of change for momentum
        if len(prices) >= 20:
            roc_20 = (prices[-1] - prices[-20]) / prices[-20]
        else:
            roc_20 = 0.0
            
        if len(prices) >= 50:
            roc_50 = (prices[-1] - prices[-50]) / prices[-50]
        else:
            roc_50 = 0.0
        
        # Price position relative to MAs
        price_above_fast = current_price > ma_fast if ma_fast else False
        price_above_medium = current_price > ma_medium if ma_medium else False
        price_above_slow = current_price > ma_slow if ma_slow else False
        
        # MA alignment (golden cross)
        ma_bullish_alignment = (ma_fast > ma_medium > ma_slow) if (ma_fast and ma_medium and ma_slow) else False
        ma_bearish_alignment = (ma_fast < ma_medium < ma_slow) if (ma_fast and ma_medium and ma_slow) else False
        
        # Calculate ADX for trend strength only
        adx, plus_di, minus_di = self._calculate_adx(highs, lows, closes, self.adx_period)
        strong_trend = adx > self.adx_threshold
        
        # Simple scoring based on TREND FOLLOWING
        confidence = 0.0
        
        # Primary signal: MA alignment and price position
        if ma_bullish_alignment:
            confidence += 0.50  # Strong bullish
            if price_above_fast and price_above_medium and price_above_slow:
                confidence += 0.30  # Very strong - price above all MAs
        
        # Momentum confirmation (more lenient)
        if roc_20 > 0:
            confidence += 0.10
        if roc_50 > 0:
            confidence += 0.10
            
        # Trend strength bonus
        if strong_trend and plus_di > minus_di:
            confidence += 0.10
        
        # Additional boost if price is above fast MA (early trend entry)
        if price_above_fast and ma_fast:
            confidence += 0.10
        
        # Bearish signals
        bearish_confidence = 0.0
        if ma_bearish_alignment:
            bearish_confidence += 0.40
            if not price_above_fast and not price_above_medium and not price_above_slow:
                bearish_confidence += 0.30
        
        if roc_20 < 0:
            bearish_confidence += 0.10
        if roc_50 < 0:
            bearish_confidence += 0.10
            
        if strong_trend and minus_di > plus_di:
            bearish_confidence += 0.10
        
        # Final confidence
        final_confidence = max(0.0, min(1.0, confidence))
        
        return {
            'adx': adx,
            'plus_di': plus_di,
            'minus_di': minus_di,
            'ma_fast': ma_fast,
            'ma_medium': ma_medium,
            'ma_slow': ma_slow,
            'roc_20': roc_20,
            'roc_50': roc_50,
            'price_above_fast': price_above_fast,
            'price_above_medium': price_above_medium,
            'price_above_slow': price_above_slow,
            'ma_bullish_alignment': ma_bullish_alignment,
            'ma_bearish_alignment': ma_bearish_alignment,
            'strong_trend': strong_trend,
            'confidence': final_confidence,
            'bearish_confidence': bearish_confidence,
            'bullish': final_confidence > self.min_trend_strength,
            'bearish': bearish_confidence > self.min_trend_strength,
            'regime': 'trending_up' if ma_bullish_alignment else ('trending_down' if ma_bearish_alignment else 'ranging'),
            'regime_strength': final_confidence
        }
    
    def _calculate_position_size(self, portfolio: Portfolio, indicators: Dict[str, Any], current_price: float) -> float:
        """Calculate adaptive position size based on regime and confidence."""
        
        confidence = indicators['confidence']
        regime = indicators['regime']
        regime_strength = indicators['regime_strength']
        
        # Base position percentage
        if regime == "trending_up":
            # Aggressive in strong uptrends
            base_pct = self.min_position_pct + (self.max_position_pct - self.min_position_pct) * regime_strength
        elif regime == "ranging":
            # Conservative in ranging markets
            base_pct = self.min_position_pct
        elif regime == "high_volatility":
            # Very conservative in high volatility
            base_pct = self.min_position_pct * 0.6
        else:
            base_pct = self.min_position_pct
        
        # Adjust by confidence
        position_pct = base_pct * confidence
        position_pct = max(self.min_position_pct * 0.5, min(self.max_position_pct, position_pct))
        
        # Calculate dollar amount
        portfolio_value = portfolio.cash + (portfolio.quantity * current_price)
        position_value = portfolio_value * position_pct
        
        # Ensure we don't exceed available cash
        position_value = min(position_value, portfolio.cash * 0.98)  # Leave 2% buffer
        
        # Convert to size
        size = position_value / current_price if current_price > 0 else 0.0
        
        return size
    
    def _should_exit_position(self, market: MarketSnapshot, portfolio: Portfolio, indicators: Dict[str, Any]) -> tuple[bool, str]:
        """SIMPLE trend-following exit: only exit on trend reversal or stop loss."""
        
        if portfolio.quantity == 0 or not self.positions:
            return False, ""
        
        current_price = market.current_price
        entry_info = self.positions[0]
        entry_price = entry_info['price']
        
        # Update highest price for trailing stop
        if self.highest_price_since_entry is None or current_price > self.highest_price_since_entry:
            self.highest_price_since_entry = current_price
        
        # Calculate gain/loss
        gain_pct = (current_price - entry_price) / entry_price
        
        # Hard stop loss only
        if gain_pct < -self.trending_stop_loss:
            return True, f"Stop loss: {gain_pct*100:.2f}%"
        
        # Exit ONLY on strong MA bearish reversal
        ma_fast = indicators.get('ma_fast')
        ma_medium = indicators.get('ma_medium')
        ma_slow = indicators.get('ma_slow')
        
        # Death cross: fast MA crosses below medium MA (moderate signal)
        if ma_fast and ma_medium and ma_slow:
            if ma_fast < ma_medium:  # Bearish crossover
                if gain_pct > 0.03:  # Exit if we have at least 3% profit
                    return True, f"MA bearish crossover: {gain_pct*100:.2f}% profit"
            # Strong reversal: fast below slow AND medium below slow
            if ma_fast < ma_slow and ma_medium < ma_slow:
                if gain_pct > -0.11:  # Exit even if small loss to avoid bigger loss
                    return True, f"Strong MA bearish reversal: {gain_pct*100:.2f}%"
        
        # Price drops significantly below slow MA (strong bearish)
        if ma_slow and current_price < ma_slow * 0.94:  # 6% below slow MA
            if gain_pct > -0.11:  # Not too deep in loss
                return True, f"Price below slow MA: {gain_pct*100:.2f}%"
        
        # Trailing stop - only activate after BIG gains
        if gain_pct > self.trailing_activation:
            trailing_drop = (self.highest_price_since_entry - current_price) / self.highest_price_since_entry
            if trailing_drop > self.trailing_distance:
                return True, f"Trailing stop: {gain_pct*100:.2f}% profit locked"
        
        return False, ""
    
    # ==================== MAIN STRATEGY LOGIC ====================
    
    def generate_signal(self, market: MarketSnapshot, portfolio: Portfolio) -> Signal:
        """Generate trading signal based on adaptive multi-indicator analysis."""
        
        current_price = market.current_price
        prices = market.prices
        
        # Update price history
        self.price_history.append(current_price)
        
        # Build high/low history (approximation from close prices)
        # In live trading, would use actual OHLC data
        if len(self.price_history) >= 2:
            recent_prices = list(self.price_history)[-20:] if len(self.price_history) >= 20 else list(self.price_history)
            self.high_history.append(max(recent_prices[-5:]) if len(recent_prices) >= 5 else current_price)
            self.low_history.append(min(recent_prices[-5:]) if len(recent_prices) >= 5 else current_price)
        else:
            self.high_history.append(current_price)
            self.low_history.append(current_price)
        
        # Validate data
        if current_price <= 0 or len(self.price_history) < 50:
            return Signal("hold", reason="Insufficient data")
        
        # Analyze indicators
        indicators = self._analyze_indicators(
            list(self.price_history),
            list(self.high_history),
            list(self.low_history),
            list(self.price_history)
        )
        
        self.current_regime = indicators['regime']
        
        self._log("ANALYSIS", 
                  f"Price=${current_price:.2f} | Regime={indicators['regime']} | "
                  f"ADX={indicators['adx']:.1f} | MA_align={indicators['ma_bullish_alignment']} | "
                  f"ROC20={indicators['roc_20']*100:.1f}% | Confidence={indicators['confidence']:.2f}")
        
        # Check for exit signals first
        if portfolio.quantity > 0:
            should_exit, exit_reason = self._should_exit_position(market, portfolio, indicators)
            if should_exit:
                sell_size = portfolio.quantity
                self._log("DECISION", f"SELL | {exit_reason}")
                return Signal("sell", size=sell_size, reason=exit_reason)
        
        # Check cooldown period
        now = datetime.now(timezone.utc)
        if self.last_trade_time:
            hours_since_trade = (now - self.last_trade_time).total_seconds() / 3600
            if hours_since_trade < self.cooldown_hours:
                return Signal("hold", reason=f"Cooldown: {hours_since_trade:.1f}h / {self.cooldown_hours}h")
        
        # Check for entry signals
        if portfolio.quantity == 0 and indicators['bullish']:
            # Additional confirmation for entry
            regime = indicators['regime']
            
            # Only avoid strong downtrends - allow ranging and moderate volatility
            if regime == "trending_down":
                return Signal("hold", reason=f"Unfavorable regime: {regime}")
            
            # Calculate position size
            size = self._calculate_position_size(portfolio, indicators, current_price)
            
            if size * current_price < 10:  # Minimum $10 trade
                return Signal("hold", reason="Position size too small")
            
            # Determine stop loss based on regime
            if regime == "trending_up":
                stop_loss_pct = self.trending_stop_loss
            else:
                stop_loss_pct = self.ranging_stop_loss
            
            target_price = current_price * (1 + stop_loss_pct * self.take_profit_multiplier)
            stop_loss_price = current_price * (1 - stop_loss_pct)
            
            self._log("DECISION", 
                     f"BUY | Regime={regime} | Confidence={indicators['confidence']:.2f} | "
                     f"Size={size:.8f} | Value=${size*current_price:.2f}")
            
            return Signal(
                "buy",
                size=size,
                reason=f"Adaptive entry: {regime} regime, confidence={indicators['confidence']:.2f}",
                target_price=target_price,
                stop_loss=stop_loss_price,
                entry_price=current_price
            )
        
        return Signal("hold", reason=f"Waiting for optimal setup | Regime={indicators['regime']} | Conf={indicators['confidence']:.2f}")
    
    def on_trade(self, signal: Signal, execution_price: float, execution_size: float, timestamp: datetime) -> None:
        """Update strategy state after trade execution."""
        
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        
        if signal.action == "buy" and execution_size > 0:
            position_info = {
                'price': execution_price,
                'size': execution_size,
                'timestamp': timestamp.isoformat(),
                'value': execution_price * execution_size,
                'regime': self.current_regime
            }
            self.positions.append(position_info)
            self.last_trade_time = timestamp
            self.highest_price_since_entry = execution_price
            
            self._log("EXEC", f"BUY {execution_size:.8f} @ ${execution_price:.2f} | Regime: {self.current_regime}")
        
        elif signal.action == "sell" and execution_size > 0:
            if self.positions:
                entry = self.positions.popleft()
                gain = ((execution_price - entry['price']) / entry['price']) * 100
                self._log("EXEC", f"SELL {execution_size:.8f} @ ${execution_price:.2f} | Gain: {gain:.2f}%")
            
            self.last_trade_time = timestamp
            self.highest_price_since_entry = None
    
    def get_state(self) -> Dict[str, Any]:
        """Serialize strategy state."""
        return {
            'positions': list(self.positions),
            'last_trade_time': self.last_trade_time.isoformat() if self.last_trade_time else None,
            'highest_price_since_entry': self.highest_price_since_entry,
            'price_history': list(self.price_history),
            'high_history': list(self.high_history),
            'low_history': list(self.low_history),
            'current_regime': self.current_regime
        }
    
    def set_state(self, state: Dict[str, Any]) -> None:
        """Restore strategy state."""
        self.positions = deque(state.get('positions', []), maxlen=10)
        
        last_trade = state.get('last_trade_time')
        if last_trade:
            dt = datetime.fromisoformat(last_trade)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            self.last_trade_time = dt
        
        self.highest_price_since_entry = state.get('highest_price_since_entry')
        self.price_history = deque(state.get('price_history', []), maxlen=300)
        self.high_history = deque(state.get('high_history', []), maxlen=300)
        self.low_history = deque(state.get('low_history', []), maxlen=300)
        self.current_regime = state.get('current_regime', 'unknown')


# Register the strategy
register_strategy("adaptive_trend_fusion", lambda cfg, ex: AdaptiveTrendFusionStrategy(cfg, ex))

