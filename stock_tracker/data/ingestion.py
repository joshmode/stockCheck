import requests
import pandas as pd
import io
from datetime import datetime, timedelta
from typing import List
from stock_tracker.core.models import Candle

buffer_mult = 2

class DataIngestor:
    def fetch_history(self, ticker: str, days: int = 300) -> List[Candle]:
        symbol = ticker.upper()
        if not symbol.endswith(".US") and not symbol.startswith("^"):
             symbol = f"{symbol}.US"
        
        url = f"https://stooq.com/q/d/l/?s={symbol}&i=d"
        
        try:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; StockTracker/1.0)"}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"http error {response.status_code} for {ticker}")
                return []
            
            content = response.content.decode('utf-8')
            if "Date,Open,High,Low,Close" not in content and "Date" not in content:
                print(f"invalid data for {ticker}")
                return []
                
            df = pd.read_csv(io.StringIO(content))
            
            if df.empty:
                return []

            df['Date'] = pd.to_datetime(df['Date'])
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days * buffer_mult)
            df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
            df = df.sort_values('Date')
            
            candles = []
            for _, row in df.iterrows():
                try:
                    c = Candle(
                        timestamp=row['Date'].to_pydatetime(),
                        open=float(row['Open']),
                        high=float(row['High']),
                        low=float(row['Low']),
                        close=float(row['Close']),
                        volume=float(row['Volume'])
                    )
                    candles.append(c)
                except Exception:
                    continue
            
            if len(candles) > days:
                return candles[-days:]
                
            return candles
            
        except Exception as e:
            print(f"fetch error {ticker}: {e}")
            return []
