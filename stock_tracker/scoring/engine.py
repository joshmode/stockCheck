from stock_tracker.regime.classifier import MarketRegime
from stock_tracker.volume.analysis import VolumeSignal
from stock_tracker.sentiment.analyzer import SentimentSignal
from stock_tracker.core.models import IndicatorState

class ScoringEngine:
    WEIGHTS = {
        MarketRegime.BULL_TREND: {"trend": 0.35, "momentum": 0.20, "volume": 0.20, "pattern": 0.15, "sentiment": 0.10},
        MarketRegime.BEAR_TREND: {"trend": 0.35, "momentum": 0.20, "volume": 0.20, "pattern": 0.15, "sentiment": 0.10},
        MarketRegime.RANGE:      {"trend": 0.10, "momentum": 0.40, "volume": 0.10, "pattern": 0.30, "sentiment": 0.10},
        MarketRegime.VOLATILE:   {"trend": 0.10, "momentum": 0.10, "volume": 0.40, "pattern": 0.10, "sentiment": 0.30},
        MarketRegime.TRANSITION: {"trend": 0.20, "momentum": 0.20, "volume": 0.20, "pattern": 0.20, "sentiment": 0.20},
        MarketRegime.UNKNOWN:    {"trend": 0.20, "momentum": 0.20, "volume": 0.20, "pattern": 0.20, "sentiment": 0.20}
    }

    def calculate_score(self, regime, patterns, volume, sentiment, data) -> float:
        w = self.WEIGHTS.get(regime, self.WEIGHTS[MarketRegime.UNKNOWN])

        trend = 0.0
        if data.ema20 and data.ema50:
            if data.ema20 > data.ema50:
                trend = 1.0
                if data.ema200 and data.ema50 <= data.ema200:
                    trend = 0.5
            elif data.ema20 < data.ema50:
                trend = -1.0
                if data.ema200 and data.ema50 >= data.ema200:
                    trend = -0.5

        momentum = 0.0
        if data.rsi is not None:
            momentum = max(-1.0, min(1.0, (data.rsi - 50) / 50.0))

            if regime == MarketRegime.RANGE:
                momentum = -momentum
            elif regime == MarketRegime.BULL_TREND:
                if data.rsi > 75: momentum = 0.0
                elif data.rsi < 40: momentum = 0.5
            elif regime == MarketRegime.BEAR_TREND:
                 if data.rsi < 25: momentum = 0.0
                 elif data.rsi > 60: momentum = -0.5

        vol_score = 0.0
        if volume.trend == "ACCUMULATION": vol_score = 1.0
        elif volume.trend == "DISTRIBUTION": vol_score = -1.0

        if volume.evr < 0.5 and volume.status == "CLIMAX":
             vol_score = -vol_score

        pat_score = 0.0
        bull = ["BOTTOM", "INVERSE", "BULL", "UPTREND"]
        bear = ["TOP", "HEAD", "BEAR", "DOWNTREND"]

        for p in patterns:
            if any(k in p for k in bull): pat_score += 1.0
            if any(k in p for k in bear): pat_score -= 1.0
        pat_score = max(-1.0, min(1.0, pat_score))

        sent_score = max(-1.0, min(1.0, sentiment.score))

        final = (
            w["trend"] * trend +
            w["momentum"] * momentum +
            w["volume"] * vol_score +
            w["pattern"] * pat_score +
            w["sentiment"] * sent_score
        )

        return max(-1.0, min(1.0, final))
