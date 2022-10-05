from xddb import EnemyTeam, PlayerTeam, QuickBattleSeedSearcher, XDDBClient
from xdrngtool import execute_automation, TargetSelector, CurrentSeedSearcher, TeamPair, SeedAdjuster

class GenerateNextTeamPair():
    def run(self) -> TeamPair:
        pass
class TransitionToQuickBattle():
    def run(self):
        return ((PlayerTeam.Mewtwo, 100, 100), (EnemyTeam.Articuno, 100, 100))
class EnterQuickBattle():
    def run(self):
        pass
class ExitQuickBattle():
    def run(self):
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

tsv = None
advances_by_opening_items = None

client = XDDBClient()
searcher = QuickBattleSeedSearcher(client, tsv) if tsv is not None else QuickBattleSeedSearcher(client)

operations = (
    GenerateNextTeamPair(),
    TransitionToQuickBattle(),
    EnterQuickBattle(),
    ExitQuickBattle(),
    SetCursorToSetting(),
    ChangeSetting(),
    Load(),
    WriteReport(),
    SetCursorToItems(),
    OpenItems(),
    WatchSteps(),
)

current_seed_searcher = CurrentSeedSearcher(searcher, operations[0])

target_selector = TargetSelector(current_seed_searcher, operations[1])
seed_adjuster = SeedAdjuster(current_seed_searcher, operations[0], *operations[2:])

execute_automation(target_selector, seed_adjuster, [], tsv, advances_by_opening_items)
