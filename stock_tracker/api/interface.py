from typing import List, Optional, Any, Dict
from dataclasses import dataclass, field
from datetime import datetime

from stock_tracker.data.ingestion import DataIngestor
from stock_tracker.structure.patterns import PatternRecognizer
from stock_tracker.structure.swings import SwingDetector
from stock_tracker.volume.analysis import VolumeAnalyzer
from stock_tracker.regime.classifier import RegimeClassifier, MarketRegime
from stock_tracker.sentiment.analyzer import SentimentAnalyzer
from stock_tracker.sentiment.news_client import NewsClient
from stock_tracker.scoring.engine import ScoringEngine
from stock_tracker.positioning.manager import PositionManager
from stock_tracker.risk.manager import RiskManager
from stock_tracker.cache.manager import LRUCache, AnalysisState
from stock_tracker.backtest_snapshot.engine import BacktestEngine
from stock_tracker.decay.aging import SignalDecay
from stock_tracker.core.models import IndicatorState, SwingPoint, Candle
from stock_tracker.indicators.streaming import EMA, RSI, ATR, MACD, VWAP, OBV, BollingerBands, ADX

@dataclass
class AnalysisReport:
    ticker: str
    timestamp: datetime
    price: float
    recommendation: str
    trade_type: str
    confidence: float
    target: float
    stop_loss: float
    risk_reward: float
    confidence_interval_low: float
    confidence_interval_high: float
    patterns: List[str]
    regime: Any
    sentiment_summary: str
    sentiment_score: float
    rationale: str
    entry_signal: str
    trend_strength: str
    volume_status: str
    volume_trend: str
    position_size_shares: int
    position_size_pct: float
    backtest_win_rate: Optional[float] = None
    backtest_avg_move: Optional[float] = None
    swings: List[SwingPoint] = field(default_factory=list)
    candles: List[Any] = field(default_factory=list)

class Context:
    def __init__(self):
        self.ema20 = EMA(20)
        self.ema50 = EMA(50)
        self.ema200 = EMA(200)
        self.rsi = RSI(14)
        self.atr = ATR(14)
        self.macd = MACD()
        self.vwap = VWAP()
        self.obv = OBV()
        self.bb = BollingerBands(20, 2.0)
        self.adx = ADX(14)

    def update(self, candle: Candle) -> IndicatorState:
        p = candle.close
        h, l, c, v = candle.high, candle.low, candle.close, candle.volume

        e20 = self.ema20.update(p)
        e50 = self.ema50.update(p)
        e200 = self.ema200.update(p)
        rsi = self.rsi.update(p)
        atr = self.atr.update(h, l, c)
        m, s, hist = self.macd.update(p)
        vwap = self.vwap.update(h, l, c, v)
        obv = self.obv.update(c, v)
        ub, lb, basis, width = self.bb.update(p)
        adx = self.adx.update(h, l, c)

        return IndicatorState(
            ema20=e20, ema50=e50, ema200=e200,
            rsi=rsi, atr=atr,
            macd_line=m, macd_signal=s, macd_hist=hist,
            vwap=vwap,
            upper_bollinger=ub, lower_bollinger=lb, bollinger_width=width,
            adx=adx, obv=obv
        )

class MarketAnalyzer:
    def __init__(self):
        self.cache = LRUCache(50)
        self.data = DataIngestor()
        self.patterns = PatternRecognizer()
        self.volume = VolumeAnalyzer()
        self.regime = RegimeClassifier()
        self.sentiment = SentimentAnalyzer()
        self.news = NewsClient()
        self.scoring = ScoringEngine()
        self.pos = PositionManager()
        self.risk = RiskManager()
        self.backtest = BacktestEngine()
        self.decay = SignalDecay()

    def analyze(self, ticker: str) -> Optional[AnalysisReport]:
        cached = self.cache.get(ticker)

        process_candles = []
        full_hist = []
        ctx = None
        detector = None
        structure = []

        lookback = 300
        raw = self.data.fetch_history(ticker, days=lookback)
        if not raw:
            return None

        if cached:
            last_dt = cached.last_updated
            process_candles = [c for c in raw if c.timestamp > last_dt]
            full_hist = raw
            ctx = cached.streaming_objects.get("indicators")
            detector = cached.streaming_objects.get("swing_detector")
            structure = list(cached.swings)
            if not ctx:
                 cached = None

        if not cached:
            process_candles = raw
            full_hist = raw
            ctx = Context()
            detector = SwingDetector()
            structure = []

        curr_ind = None
        last = None

        for i, c in enumerate(process_candles):
            curr_ind = ctx.update(c)
            swing = detector.update(c, i)
            if swing:
                structure.append(swing)
            last = c

        if not curr_ind:
            if cached:
                curr_ind = cached.indicators
                if not process_candles and full_hist:
                     last = full_hist[-1]
            else:
                 return None

        if not last:
            if full_hist:
                 last = full_hist[-1]
            else:
                 return None

        pats = self.patterns.detect_patterns(structure)
        regime = self.regime.classify(curr_ind)

        avg_vol = last.volume
        if len(full_hist) > 0:
             recent = full_hist[-20:]
             avg_vol = sum(c.volume for c in recent) / len(recent)

        change = last.close - last.open
        vol_sig = self.volume.analyze(last, avg_vol, last.open, curr_ind.atr or 1.0)

        headlines = self.news.fetch_headlines(ticker)
        sent_sig = self.sentiment.analyze(headlines)

        score = self.scoring.calculate_score(regime, pats, vol_sig, sent_sig, curr_ind)
        rec = self.pos.recommend(score, regime, curr_ind, pats, last.close)

        risk_dir = rec.type
        risk_conf = rec.confidence

        if risk_dir not in ["LONG", "SHORT"]:
            risk_dir = "LONG"
            risk_conf = 0.5
            if regime == MarketRegime.BEAR_TREND:
                risk_dir = "SHORT"

        prev = full_hist[-2] if len(full_hist) >= 2 else None

        # RiskManager.calculate_risk(price, atr, direction, confidence, swings, prev_candle)
        risk_prof = self.risk.calculate_risk(last.close, curr_ind.atr or 0, risk_dir, risk_conf, structure, prev)

        stats = self.backtest.get_stats(pats, regime)

        new_state = AnalysisState(
            ticker=ticker,
            last_updated=datetime.now(),
            indicators=curr_ind,
            swings=structure,
            last_score=score,
            sentiment_score=sent_sig.score,
            last_price=last.close,
            streaming_objects={
                "indicators": ctx,
                "swing_detector": detector
            }
        )
        self.cache.put(ticker, new_state)

        atr = curr_ind.atr or (last.close * 0.02)
        low_ci = last.close - (2.0 * atr)
        high_ci = last.close + (2.0 * atr)

        return AnalysisReport(
            ticker=ticker,
            timestamp=datetime.now(),
            price=last.close,
            recommendation=rec.action,
            trade_type=rec.type,
            confidence=rec.confidence,
            target=risk_prof.target,
            stop_loss=risk_prof.stop_loss,
            risk_reward=risk_prof.risk_reward_ratio,
            confidence_interval_low=low_ci,
            confidence_interval_high=high_ci,
            patterns=pats,
            regime=regime,
            sentiment_summary=sent_sig.summary,
            sentiment_score=sent_sig.score,
            rationale=rec.rationale,
            entry_signal=rec.entry_signal,
            trend_strength=f"ADX {curr_ind.adx:.1f}" if curr_ind.adx else "N/A",
            volume_status=vol_sig.status,
            volume_trend=vol_sig.trend,
            position_size_shares=risk_prof.suggested_shares,
            position_size_pct=risk_prof.max_position_size_pct,
            backtest_win_rate=stats.win_rate if stats else None,
            backtest_avg_move=stats.avg_move if stats else None,
            swings=structure,
            candles=full_hist
        )

StockTracker = MarketAnalyzer
