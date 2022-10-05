from typing import List
from .seed_adjuster import SeedAdjuster
from .target_selector import TargetSelector

def execute_automation(
    target_selector: TargetSelector, 
    seed_adjuster: SeedAdjuster, 
    target_seeds: List[int], 
):
    """ポケモンXDの乱数調整を行う。

    Args:
        target_selector (TargetSelector): 
        seed_adjuster (SeedAdjuster): 
        target_seeds (List[int]): 目標seedのリスト
    """
    current_seed, target = target_selector.execute(target_seeds)
    try:
        seed_adjuster.execute(target)
    except:
        execute_automation(target_selector, seed_adjuster, target_seeds)
