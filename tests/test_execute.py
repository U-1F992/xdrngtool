from tkinter.filedialog import Open
from xddb import QuickBattleSeedSearcher, XDDBClient
from xdrngtool import execute, TargetDecider, CurrentSeedSearcher, TeamPair, Advancer

class GenerateNextTeamPair():
    def run(self) -> TeamPair:
        pass
class TransitionToQuickBattle():
    def run(self):
        pass
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

generate_next_team_pair = GenerateNextTeamPair()
transition_to_quick_battle = TransitionToQuickBattle()
enter_quick_battle = EnterQuickBattle()
exit_quick_battle = ExitQuickBattle()
set_cursor_to_setting = SetCursorToSetting()
change_setting = ChangeSetting()
load = Load()
write_report = WriteReport()
set_cursor_to_items = SetCursorToItems()
open_items = OpenItems()
watch_steps = WatchSteps()

current_seed_searcher = CurrentSeedSearcher(searcher, generate_next_team_pair)

target_decider = TargetDecider(current_seed_searcher, transition_to_quick_battle)
advancer = Advancer(current_seed_searcher, generate_next_team_pair, enter_quick_battle, exit_quick_battle, set_cursor_to_setting, change_setting, load, write_report, set_cursor_to_items, open_items, watch_steps)

execute(target_decider, advancer, [], tsv, advances_by_opening_items)
