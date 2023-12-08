from abc import abstractmethod
from typing import List

from mobile_env.core.entities import BaseStation


class Scheduler:
    def __init__(self, **kwargs):
        pass

    def reset(self) -> None:
        pass

    @abstractmethod
    def share(self, bs: BaseStation, rates: List[float]) -> List[float]:
        pass


class ResourceFair(Scheduler):
    def share(self, bs: BaseStation, rates: List[float]) -> List[float]:
        return [rate / len(rates) for rate in rates]

class RateFair(Scheduler):
    def share(self, bs: BaseStation, rates: List[float]) -> List[float]:
        total_inv_rate = sum([1 / rate for rate in rates])
        return 1 / total_inv_rate

class MyScheduler(Scheduler):
    def share(self, bs: BaseStation, rates: List[float]) -> List[float]:
        import random
        # Generate a random number between 0.3 and 0.7
        random_number = random.uniform(0.3, 0.7)
        rate0 = rates[0]*random_number
        rete1 = rates[1]*(1-random_number)

        return [rate0, rete1]

