from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from enum import Enum

@dataclass(frozen=True)
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

@dataclass
class IndicatorState:
    ema20: Optional[float] = None
    ema50: Optional[float] = None
    ema200: Optional[float] = None
    rsi: Optional[float] = None
    atr: Optional[float] = None
    macd_line: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None
    vwap: Optional[float] = None
    upper_bollinger: Optional[float] = None
    lower_bollinger: Optional[float] = None
    bollinger_width: Optional[float] = None
    adx: Optional[float] = None
    obv: Optional[float] = None

class SwingType(Enum):
    HIGH = "HIGH"
    LOW = "LOW"

@dataclass(frozen=True)
class SwingPoint:
    price: float
    index: int
    timestamp: datetime
    type: SwingType

@dataclass
class Signal:
    score: float
    confidence: float
    direction: str
    rationale: List[str] = field(default_factory=list)
