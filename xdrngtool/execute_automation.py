from typing import List, Optional, Tuple

from xddb import XDDBClient, QuickBattleSeedSearcher

from .automation_executor import AutomationExecutor
from .current_seed_searcher import CurrentSeedSearcher
from .protocol import Operation, OperationReturnsTeamPair, OperationTakesTimedelta
from .seed_adjuster import SeedAdjuster
from .target_selector import TargetSelector

def execute_automation(
    operations: Tuple[Operation, OperationReturnsTeamPair, OperationTakesTimedelta, Operation, Operation, Operation, Operation],
    target_seeds: List[int],
    tsv: Optional[int] = None,
    advances_by_opening_items: Optional[int] = None,
):
    """ポケモンXDの乱数調整を行う。

    Args:
        operations (Tuple[Operation, OperationReturnsTeamPair, OperationTakesTimedelta, Operation, Operation, Operation, Operation]): 
        target_seeds (List[int]): 目標のseed
        tsv (Optional[int], optional): TSV。正確に指定されない場合、実際のいますぐバトルの生成結果および回数は異なる可能性が生じる。 Defaults to None.
        advances_by_opening_items (Optional[int], optional): 「もちもの」の開閉にかかる消費数。レポートを消費手段に加える場合のみ指定する。 Defaults to None.
    """
    
    client = XDDBClient()
    searcher = QuickBattleSeedSearcher(client, tsv) if tsv is not None else QuickBattleSeedSearcher(client)

    current_seed_searcher = CurrentSeedSearcher(searcher, operations[1])

    target_selector = TargetSelector(current_seed_searcher, operations[0])
    seed_adjuster = SeedAdjuster(current_seed_searcher, *operations[1:], tsv, advances_by_opening_items)

    automation_executor = AutomationExecutor(target_selector, seed_adjuster)
    automation_executor.execute(target_seeds)
    