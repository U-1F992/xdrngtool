from typing import List
from .seed_adjuster import SeedAdjuster
from .target_selector import TargetSelector

class AutomationExecutor():
    def __init__(self, target_selector: TargetSelector, seed_adjuster: SeedAdjuster, ) -> None:
        """
        Args:
            target_selector (TargetSelector): 
            seed_adjuster (SeedAdjuster): 
        """
        self.__target_selector = target_selector
        self.__seed_adjuster = seed_adjuster
    def execute(self, target_seeds: List[int]):
        """ポケモンXDの乱数調整を行う。

        Args:
            target_seeds (List[int]): 目標seedのリスト
        """
        current_seed, target = self.__target_selector.execute(target_seeds)
        try:
            self.__seed_adjuster.execute(target)
        except:
            self.execute(target_seeds)
