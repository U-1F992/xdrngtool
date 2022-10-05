from typing import List, Optional
from .seed_adjuster import SeedAdjuster
from .target_selector import TargetSelector

def execute_automation(
    target_selector: TargetSelector, 
    seed_adjuster: SeedAdjuster, 
    target_seeds: List[int], 
    tsv: Optional[int] = None, 
    advances_by_opening_items: Optional[int] = None
):
    """ポケモンXDの乱数調整を行う。

    Args:
        target_selector (TargetSelector): 
        seed_adjuster (SeedAdjuster): 
        target_seeds (List[int]): 目標seedのリスト
        tsv (Optional[int], optional): TSV。指定しない場合、いますぐバトルの生成結果に齟齬が生じ再計算が発生する可能性があります。 Defaults to None.
        advances_by_opening_items (Optional[int], optional): もちものを開く際の消費数。 Defaults to None.
    """
    current_seed, target = target_selector.execute(target_seeds)
    try:
        seed_adjuster.execute(target, tsv, advances_by_opening_items)
    except:
        execute_automation(target_selector, seed_adjuster, target_seeds, tsv)
