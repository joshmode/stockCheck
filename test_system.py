import sys
import os
from datetime import datetime

sys.path.append(os.getcwd())

from stock_tracker.api.interface import MarketAnalyzer
from stock_tracker.core.models import Candle

def main():
    print("Running Verification...")

    analyzer = MarketAnalyzer()

    print("Mocking Data...")
    def mock_fetch(ticker, days=300):
        candles = []
        for i in range(days):
            price = 100.0 + (i * 0.1)
            if i > 250:
                price = 125.0 - ((i-250) * 0.5)

            c = Candle(
                timestamp=datetime.now(),
                open=float(price),
                high=float(price + 1.0),
                low=float(price - 1.0),
                close=float(price),
                volume=float(1000 + (i * 10))
            )
            candles.append(c)
        return candles

    analyzer.data.fetch_history = mock_fetch

    ticker = "TEST_TICKER"
    print(f"Analyzing {ticker}...")
    report = analyzer.analyze(ticker)

    if report:
        print("Success!")
        print(f"Ticker: {report.ticker}")
        print(f"Rec: {report.recommendation}")
        print(f"Price: {report.price:.2f}")
        print(f"Target: {report.target:.2f}")
        print(f"Stop: {report.stop_loss:.2f}")
        print(f"Patterns: {report.patterns}")
        print(f"Swings: {len(report.swings)}")
        print(f"Regime: {report.regime}")
        print(f"Rationale: {report.rationale}")
    else:
        print("Failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
