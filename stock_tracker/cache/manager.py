from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, List
from stock_tracker.core.models import IndicatorState, SwingPoint

@dataclass
class AnalysisState:
    """
    Snapshot of analysis for a ticker to support incremental updates.
    """
    ticker: str
    last_updated: datetime
    indicators: IndicatorState
    swings: List[SwingPoint]
    last_score: float
    sentiment_score: Optional[float] = None
    last_price: Optional[float] = None
    streaming_objects: Optional[Any] = None # Holds stateful indicator instances

class LRUCache:
    def __init__(self, capacity: int = 50):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: str) -> Optional[AnalysisState]:
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: str, value: AnalysisState) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
