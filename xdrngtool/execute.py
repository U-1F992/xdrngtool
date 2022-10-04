from typing import List, Optional
from .advancer import Advancer
from .target_decider import TargetDecider

def execute(
    target_decider: TargetDecider, 
    advancer: Advancer, 
    target_seeds: List[int], 
    tsv: Optional[int] = None, 
    advances_by_opening_items: Optional[int] = None
):
    """ポケモンXDの乱数調整を行う。

    Args:
        target_decider (TargetDecider): 
        advancer (Advancer): 
        target_seeds (List[int]): 目標seedのリスト
        tsv (Optional[int], optional): TSV。指定しない場合、いますぐバトルの生成結果に齟齬が生じ再計算が発生する可能性があります。 Defaults to None.
        advances_by_opening_items (Optional[int], optional): もちものを開く際の消費数。 Defaults to None.
    """
    current_seed, target = target_decider.execute(target_seeds)
    try:
        advancer.execute(target, tsv, advances_by_opening_items)
    except:
        execute(target_decider, advancer, target_seeds, tsv)
