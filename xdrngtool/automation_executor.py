from typing import List
from .protocol import ISeedAdjuster, ITargetSelector

class AutomationExecutor():
    def __init__(self, target_selector: ITargetSelector, seed_adjuster: ISeedAdjuster, ) -> None:
        """
        Args:
            target_selector (ITargetSelector): 
            seed_adjuster (ISeedAdjuster): 
        """
        self.__target_selector = target_selector
        self.__seed_adjuster = seed_adjuster
    def execute(self, target_seeds: List[int]):
        """ポケモンXDの乱数調整を行う。

        Args:
            target_seeds (List[int]): 目標seedのリスト
        """
        current_seed, target = self.__target_selector.execute(target_seeds)
        self.__seed_adjuster.execute(target)
