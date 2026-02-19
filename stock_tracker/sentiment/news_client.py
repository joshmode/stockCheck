import os
import requests
from typing import List
from datetime import datetime, timedelta

class NewsClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2/everything"

    def fetch_headlines(self, query: str, days: int = 2) -> List[str]:
        if not self.api_key:
            return self._mock(query)

        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            params = {
                'q': query,
                'from': from_date,
                'sortBy': 'relevancy',
                'language': 'en',
                'apiKey': self.api_key,
                'pageSize': 20
            }

            response = requests.get(self.base_url, params=params)
            response.raise_for_status()

            data = response.json()
            articles = data.get('articles', [])

            headlines = [article['title'] for article in articles if article.get('title')]
            return headlines

        except Exception:
            return []

    def _mock(self, query: str) -> List[str]:
        return [
            f"{query} earnings report.",
            f"Analysts upgrade {query}.",
            f"{query} stock price volatility.",
            f"{query} product launch.",
            f"Regulatory news for {query}."
        ]
