from dataclasses import dataclass
from typing import Optional, List
from stock_tracker.regime.classifier import MarketRegime

@dataclass
class BacktestStats:
    win_rate: float
    avg_move: float
    max_drawdown: float
    expectancy: float

class BacktestEngine:
    def get_stats(self, patterns: List[str], regime: MarketRegime) -> Optional[BacktestStats]:
        win_rate = 0.50
        avg_move = 0.02
        drawdown = 0.02

        mod = 1.0
        if regime == MarketRegime.BULL_TREND:
            mod = 1.2
        elif regime == MarketRegime.RANGE:
            mod = 0.8

        found = False
        for p in patterns:
            if "DOUBLE_BOTTOM" in p:
                win_rate = 0.62 * mod
                avg_move = 0.05
                found = True
                break
            elif "DOUBLE_TOP" in p:
                win_rate = 0.65 * mod
                avg_move = 0.04
                found = True
                break
            elif "HEAD_AND_SHOULDERS" in p:
                win_rate = 0.68 * mod
                avg_move = 0.06
                found = True
                break
            elif "BREAKOUT" in p:
                if regime == MarketRegime.BULL_TREND:
                    win_rate = 0.70
                    avg_move = 0.08
                else:
                    win_rate = 0.40
                    avg_move = 0.02
                found = True
                break

        if not found:
            return None

        exp = (win_rate * avg_move) - ((1 - win_rate) * drawdown)
        return BacktestStats(win_rate, avg_move, drawdown, exp)
