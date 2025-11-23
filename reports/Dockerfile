# Backtest Runner - Dockerfile
FROM python:3.11-slim

LABEL description="Backtest Runner for Adaptive Trend Fusion Strategy"
LABEL purpose="contest_validation"

# Set working directory
WORKDIR /app

# Copy base bot infrastructure
COPY base-bot-template/ /app/base-bot-template/

# Copy strategy files
COPY adaptive-trend-fusion-strategy/ /app/adaptive-trend-fusion-strategy/

# Copy reports/backtest files
COPY reports/ /app/reports/

# Install dependencies
RUN pip install --no-cache-dir -r /app/base-bot-template/requirements.txt

# Install additional backtest dependencies
RUN pip install --no-cache-dir yfinance pandas

# Set working directory to reports
WORKDIR /app/reports

# Make backtest runner executable
RUN chmod +x /app/reports/backtest_runner.py

# Run backtest
CMD ["python", "/app/reports/backtest_runner.py"]


