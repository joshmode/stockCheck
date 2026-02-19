from dataclasses import dataclass
from typing import List
from stock_tracker.core.models import IndicatorState
from stock_tracker.regime.classifier import MarketRegime

@dataclass
class PositionRecommendation:
    action: str
    type: str
    confidence: float
    rationale: str
    entry_signal: str

class PositionManager:
    def recommend(self, score: float, regime: MarketRegime,
                 data: IndicatorState, patterns: List[str],
                 price: float) -> PositionRecommendation:

        bias = "NEUTRAL"
        if score > 0.4: bias = "BULLISH"
        elif score < -0.4: bias = "BEARISH"

        if bias == "NEUTRAL":
            return PositionRecommendation("HOLD", "NEUTRAL", 0.0, "neutral score", "NONE")

        action = "HOLD"
        trade_type = "NEUTRAL"
        rationale = ""
        entry_signal = "NONE"
        confidence = abs(score)

        if bias == "BULLISH":
            if regime in [MarketRegime.BULL_TREND, MarketRegime.TRANSITION]:
                action = "BUY"
                trade_type = "LONG_SWING"
                rationale = "trend continuation"

                if data.ema20 and price < data.ema20 * 1.02:
                     entry_signal = "PULLBACK_EMA20"
                else:
                     entry_signal = "BREAKOUT"

            elif regime == MarketRegime.RANGE:
                if data.rsi and data.rsi < 40:
                    action = "BUY"
                    trade_type = "LONG_MEAN_REVERT"
                    rationale = "range support buy"
                    entry_signal = "REVERSAL"
                else:
                    rationale = "bullish but ranging"

            elif regime == MarketRegime.BEAR_TREND:
                if any("BOTTOM" in p or "INVERSE" in p for p in patterns):
                    action = "BUY"
                    trade_type = "LONG_REVERSAL"
                    rationale = "counter-trend pattern"
                    entry_signal = "BREAKOUT"
                else:
                    rationale = "bullish score vs bear trend"

        elif bias == "BEARISH":
            if regime in [MarketRegime.BEAR_TREND, MarketRegime.TRANSITION]:
                action = "SELL"
                trade_type = "SHORT_SWING"
                rationale = "trend continuation down"

                if data.ema20 and price > data.ema20 * 0.98:
                    entry_signal = "PULLBACK_EMA20"
                else:
                    entry_signal = "BREAKDOWN"

            elif regime == MarketRegime.RANGE:
                if data.rsi and data.rsi > 60:
                    action = "SELL"
                    trade_type = "SHORT_MEAN_REVERT"
                    rationale = "range resistance sell"
                    entry_signal = "REVERSAL"
                else:
                    rationale = "bearish but ranging"

            elif regime == MarketRegime.BULL_TREND:
                if any("TOP" in p or "HEAD" in p for p in patterns):
                    action = "SELL"
                    trade_type = "SHORT_REVERSAL"
                    rationale = "top pattern in trend"
                    entry_signal = "BREAKDOWN"
                else:
                    rationale = "bearish score vs bull trend"

        if action == "HOLD":
            trade_type = "NEUTRAL"

        return PositionRecommendation(action, trade_type, confidence, rationale, entry_signal)
