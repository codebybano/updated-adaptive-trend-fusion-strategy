#!/usr/bin/env python3
"""Adaptive Trend Fusion Strategy Bot - Startup Script."""

from __future__ import annotations

import sys
import os

# Import base infrastructure from base-bot-template
# Handle both local development and Docker container paths
base_path = os.path.join(os.path.dirname(__file__), '..', 'base-bot-template')
if not os.path.exists(base_path):
    # In Docker container, base template is at /app/base/
    base_path = '/app/base'

sys.path.insert(0, base_path)

# Import Adaptive Trend Fusion strategy (this registers the strategy)
import adaptive_trend_fusion_strategy

# Import base bot infrastructure
from universal_bot import UniversalBot


def main() -> None:
    """Main entry point for Adaptive Trend Fusion Bot."""
    config_path = sys.argv[1] if len(sys.argv) > 1 else None

    bot = UniversalBot(config_path)

    # Print startup info with unique identifiers
    print("=" * 70)
    print("🚀 ADAPTIVE TREND FUSION TRADING BOT")
    print("=" * 70)
    print(f"🆔 Bot ID: {bot.config.bot_instance_id}")
    print(f"👤 User ID: {bot.config.user_id}")
    print(f"📈 Strategy: {bot.config.strategy}")
    print(f"💰 Symbol: {bot.config.symbol}")
    print(f"🏦 Exchange: {bot.config.exchange}")
    print(f"💵 Starting Cash: ${bot.config.starting_cash:,.2f}")
    print("=" * 70)
    print("🎯 STRATEGY: Adaptive Trend Fusion System")
    print("📊 INDICATORS: Stochastic, ADX, Williams %R, MAs")
    print("🧠 APPROACH: Regime-adaptive with dynamic position sizing")
    print("🛡️  RISK: Regime-specific stops & trailing management")
    print("💎 TARGET: Achieve >30% returns with <50% drawdown")
    print("=" * 70)

    bot.run()


if __name__ == "__main__":
    main()


