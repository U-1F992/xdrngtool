from datetime import timedelta
from time import sleep
from typing import List, Optional
from xddb import EnemyTeam, PlayerTeam, QuickBattleSeedSearcher, XDDBClient
from xdrngtool import AutomationExecutor, TargetSelector, CurrentSeedSearcher, TeamPair, SeedAdjuster


def _indicate(obj):
    print(f"{obj.__class__.__name__} called")
    sleep(0.3)

class TransitionToQuickBattle():
    def run(self):
        _indicate(self)
        pass
class GenerateNextTeamPair():
    def run(self) -> TeamPair:
        _indicate(self)
        return ((PlayerTeam.Mewtwo, 100, 100), (EnemyTeam.Articuno, 100, 100))
class EnterWaitAndExitQuickBattle():
    def run(self, td: timedelta):
        _indicate(self)
        pass
class SetCursorToSetting():
    def run(self):
        pass
class ChangeSetting():
    def run(self):
        pass
class Load():
    def run(self):
        pass
class WriteReport():
    def run(self):
        pass
class SetCursorToItems():
    def run(self):
        pass
class OpenItems():
    def run(self):
        pass
class WatchSteps():
    def run(self):
        pass

operations = (
    TransitionToQuickBattle(),
    GenerateNextTeamPair(),
    EnterWaitAndExitQuickBattle(),
    SetCursorToSetting(),
    ChangeSetting(),
    Load(),
    WriteReport(),
)

target_seeds: List[int] = [0xbeef]
tsv: Optional[int] = None
advances_by_opening_items: Optional[int] = None

client = XDDBClient()
searcher = QuickBattleSeedSearcher(client, tsv) if tsv is not None else QuickBattleSeedSearcher(client)

current_seed_searcher = CurrentSeedSearcher(searcher, operations[1])

target_selector = TargetSelector(current_seed_searcher, operations[0])
seed_adjuster = SeedAdjuster(current_seed_searcher, *operations[1:], tsv, advances_by_opening_items)

automation_executor = AutomationExecutor(target_selector, seed_adjuster)
automation_executor.execute(target_seeds)
