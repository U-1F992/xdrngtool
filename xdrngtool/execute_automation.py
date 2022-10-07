

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
    
    client = XDDBClient()
    searcher = QuickBattleSeedSearcher(client, tsv) if tsv is not None else QuickBattleSeedSearcher(client)

    current_seed_searcher = CurrentSeedSearcher(searcher, operations[1])

    target_selector = TargetSelector(current_seed_searcher, operations[0])
    seed_adjuster = SeedAdjuster(current_seed_searcher, *operations[1:], tsv, advances_by_opening_items)

    automation_executor = AutomationExecutor(target_selector, seed_adjuster)
    automation_executor.execute(target_seeds)
    