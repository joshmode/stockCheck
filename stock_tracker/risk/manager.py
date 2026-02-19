from dataclasses import dataclass
from typing import List, Optional
from stock_tracker.core.models import SwingPoint, SwingType, Candle

@dataclass
class RiskProfile:
    stop_loss: float
    target: float
    trailing_stop_dist: float
    risk_reward_ratio: float
    suggested_shares: int
    max_position_size_pct: float

class RiskManager:
    def __init__(self, equity: float = 100000.0, risk_per_trade: float = 0.01):
        self.equity = equity
        self.risk_per_trade = risk_per_trade

    def check_tradeability(self, price: float, avg_vol: float, vol: float) -> bool:
        if (price * avg_vol) < 2000000:
            return False
        if vol <= 0 or (vol / price) < 0.005:
            return False
        return True

    def calculate_risk(self, price: float, atr: float, direction: str = "LONG", confidence: float = 1.0, swings: List[SwingPoint] = None, prev_candle: Optional[Candle] = None) -> RiskProfile:
        if direction not in ["LONG", "SHORT"]:
            return RiskProfile(0.0, 0.0, 0.0, 0.0, 0, 0.0)

        if atr <= 0:
            atr = price * 0.02

        stop = 0.0
        target = 0.0

        pivot = 0.0
        r1 = 0.0
        s1 = 0.0

        if prev_candle:
            pivot = (prev_candle.high + prev_candle.low + prev_candle.close) / 3.0
            r1 = (2.0 * pivot) - prev_candle.low
            s1 = (2.0 * pivot) - prev_candle.high

        buffer = atr * 0.5

        if direction == "LONG":
            found_support = False
            support = price

            if swings:
                valid = [s.price for s in swings if s.type == SwingType.LOW and s.price < price]
                if valid:
                    support = max(valid)
                    found_support = True

            if found_support and (price - support) > buffer:
                stop = support - buffer
            elif prev_candle and s1 < price:
                 stop = s1
                 dist = price - stop
                 if dist > (atr * 3.0) or dist < (atr * 0.5):
                     stop = price - (atr * 2.0)
            else:
                stop = price - (atr * 2.0)

            found_res = False
            resistance = price

            if swings:
                valid = [s.price for s in swings if s.type == SwingType.HIGH and s.price > price]
                if valid:
                    resistance = min(valid)
                    found_res = True

            if found_res and (resistance - price) > atr:
                target = resistance
            elif prev_candle and r1 > price:
                target = r1
                dist = target - price
                if dist < atr:
                     target = price + (atr * 3.0)
            else:
                target = price + (atr * 3.0)

        else:
            found_res = False
            resistance = price

            if swings:
                valid = [s.price for s in swings if s.type == SwingType.HIGH and s.price > price]
                if valid:
                    resistance = min(valid)
                    found_res = True

            if found_res and (resistance - price) > buffer:
                stop = resistance + buffer
            elif prev_candle and r1 > price:
                stop = r1
                dist = stop - price
                if dist > (atr * 3.0) or dist < (atr * 0.5):
                     stop = price + (atr * 2.0)
            else:
                stop = price + (atr * 2.0)

            found_support = False
            support = price

            if swings:
                valid = [s.price for s in swings if s.type == SwingType.LOW and s.price < price]
                if valid:
                    support = max(valid)
                    found_support = True

            if found_support and (price - support) > atr:
                target = support
            elif prev_candle and s1 < price:
                target = s1
                dist = price - target
                if dist < atr:
                     target = price - (atr * 3.0)
            else:
                target = price - (atr * 3.0)

        loss = abs(price - stop)
        profit = abs(target - price)

        rr = 0.0
        if loss > 0:
            rr = profit / loss

        win_prob = max(0.1, min(0.9, confidence))
        loss_prob = 1.0 - win_prob

        kelly = 0.0
        if rr > 0:
            kelly = win_prob - (loss_prob / rr)

        optimal_f = max(0.0, kelly * 0.5)
        risk_amt = self.equity * optimal_f
        max_risk = self.equity * self.risk_per_trade
        risk_amt = min(risk_amt, max_risk)

        size = 0
        if loss > 0 and risk_amt > 0:
            size = int(risk_amt / loss)

        val = size * price
        impact = 0.0
        if self.equity > 0:
            impact = val / self.equity

        return RiskProfile(stop, target, loss, rr, size, impact)
