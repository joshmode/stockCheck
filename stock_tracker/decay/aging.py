import math
from typing import Optional

class SignalDecay:
    def calculate_decay(self, score: float, age: float, half_life: float = 3.0) -> float:
        if age <= 0:
            return score

        k = math.log(2) / half_life
        return score * math.exp(-k * age)
