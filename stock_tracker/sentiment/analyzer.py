from dataclasses import dataclass
from typing import List
import logging

logging.getLogger("transformers").setLevel(logging.ERROR)

@dataclass
class SentimentSignal:
    score: float
    summary: str
    confidence: float

class SentimentAnalyzer:
    def __init__(self):
        self.use_bert = False
        self.classifier = None

        try:
            from transformers import pipeline
            self.classifier = pipeline("sentiment-analysis", model="ProsusAI/finbert", truncation=True)
            self.use_bert = True
        except Exception:
            try:
                from textblob import TextBlob
                self.textblob = TextBlob
            except ImportError:
                 self.textblob = None

    def analyze(self, headlines: List[str]) -> SentimentSignal:
        if not headlines:
            return SentimentSignal(0.0, "NEUTRAL", 0.0)

        total_score = 0.0
        total_conf = 0.0

        headlines = headlines[:10]

        if self.use_bert:
            try:
                results = self.classifier(headlines)

                for i, res in enumerate(results):
                    weight = 1.0 / (i + 1)
                    label = res['label'].lower()
                    score = res['score']

                    val = 0.0
                    if label == 'positive':
                        val = 1.0
                    elif label == 'negative':
                        val = -1.0

                    total_score += val * score * weight
                    total_conf += score * weight

                avg_score = total_score / total_conf if total_conf > 0 else 0.0

            except Exception:
                return self._analyze_fallback(headlines)
        else:
            return self._analyze_fallback(headlines)

        summary = "NEUTRAL"
        if avg_score > 0.15:
            summary = "POSITIVE"
        elif avg_score < -0.15:
            summary = "NEGATIVE"

        return SentimentSignal(avg_score, summary, 1.0 if self.use_bert else 0.5)

    def _analyze_fallback(self, headlines: List[str]) -> SentimentSignal:
        if not hasattr(self, 'textblob') or not self.textblob:
             return SentimentSignal(0.0, "NEUTRAL", 0.0)

        total_score = 0.0
        for h in headlines:
            blob = self.textblob(h)
            total_score += blob.sentiment.polarity

        avg_score = total_score / len(headlines)

        summary = "NEUTRAL"
        if avg_score > 0.1:
            summary = "POSITIVE"
        elif avg_score < -0.1:
            summary = "NEGATIVE"

        return SentimentSignal(avg_score, summary, 0.5)
