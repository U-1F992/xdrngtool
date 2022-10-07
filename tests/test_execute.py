from datetime import timedelta
from typing import List, Optional
from xddb import EnemyTeam, PlayerTeam, QuickBattleSeedSearcher, XDDBClient
from xdrngtool import AutomationExecutor, TargetSelector, CurrentSeedSearcher, TeamPair, SeedAdjuster

class TransitionToQuickBattle():
    """リセットし、1回いますぐバトル（さいきょう）を生成した画面まで誘導する。
    """
    def run(self):
        pass
class GenerateNextTeamPair():
    """現在のいますぐバトル生成結果を破棄し、再度生成する。
    """
    def run(self) -> TeamPair:
        return ((PlayerTeam.Mewtwo, 100, 100), (EnemyTeam.Articuno, 100, 100))
class EnterWaitAndExitQuickBattle():
    """「このポケモンで　はじめてもよいですか？」「はい」からいますぐバトルを開始し、降参「はい」まで誘導。timedelta時間待機した後、いますぐバトルを降参し、1回いますぐバトルを生成する。
    """
    def run(self, td: timedelta):
        pass
class SetCursorToSetting():
    """いますぐバトル生成済み画面から、「せってい」にカーソルを合わせる。
    """
    def run(self):
        pass
class ChangeSetting():
    """「せってい」にカーソルが合った状態から、設定を変更して保存、「せってい」にカーソルを戻す。
    """
    def run(self):
        pass
class Load():
    """「せってい」にカーソルが合った状態からロードし、メニューを開き「レポート」にカーソルを合わせる。
    """
    def run(self):
        pass
class WriteReport():
    """「レポート」にカーソルが合った状態から、レポートを書き、「レポート」にカーソルを戻す。
    """
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
