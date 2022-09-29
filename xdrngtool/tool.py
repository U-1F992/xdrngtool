from typing import List

from .abc import XDRNGOperations
from .constant import DEFAULT_TSV
from .helper import *

def execute_operation(
    operations: XDRNGOperations, 
    target_seeds: List[int], 
    tsv: int = DEFAULT_TSV, 
    advances_by_opening_items: Optional[int] = None, 
) -> bool:
    """ポケモンXDの乱数調整を行います。

    Args:
        operations (XDRNGOperations): XDRNGOperations抽象クラスを継承したクラスのオブジェクト
        target_seeds (List[int]): 目標seedのリスト
        tsv (int): TSV。指定しない場合、いますぐバトルの生成結果に齟齬が生じ再計算が発生する可能性があります。 Defaults to DEFAULT_TSV.
        advances_by_opening_items (Optional[int]): もちものを開く際の消費数。 Defaults to None.

    Returns:
        bool: 試行の成否
    """
    
    current_seed, target = decide_target(operations, target_seeds, tsv)
    
    try:
        current_seed = advance_by_moltres(operations, target, tsv)
        advance_according_to_route(current_seed, target, tsv, advances_by_opening_items)
    except:
        return execute_operation(operations, target_seeds, tsv, advances_by_opening_items)
    
    return operations.verify()
