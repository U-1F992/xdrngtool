from datetime import timedelta
from typing import List, Optional
import unittest

from xdrngtool import TeamPair

from mocks import MockGame
from xdrngtool.execute_automation import execute_automation


class TransitionToQuickBattle():
    """リセットし、1回いますぐバトル（さいきょう）を生成した画面まで誘導する。
    """
    def __init__(self, game: MockGame) -> None:
        self.__game = game
    def run(self):
        print("\n----------------------------------------\n")
        self.__game.reset()

class GenerateNextTeamPair():
    """現在のいますぐバトル生成結果を破棄し、再度生成する。
    """
    def __init__(self, game: MockGame) -> None:
        self.__game = game
    def run(self) -> TeamPair:
        ret = self.__game.generate_quick_battle()
        print(ret)
        return ret

class EnterWaitAndExitQuickBattle():
    """「このポケモンで　はじめてもよいですか？」「はい」からいますぐバトルを開始し、降参「はい」まで誘導。timedelta時間待機した後、いますぐバトルを降参し、1回いますぐバトルを生成する。
    """
    def __init__(self, game: MockGame) -> None:
        self.__game = game
    def run(self, td: timedelta):
        self.__game.show_moltres(td)
        print("~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ")

class SetCursorToSetting():
    """いますぐバトル生成済み画面から、「せってい」にカーソルを合わせる。
    """
    def __init__(self, game: MockGame) -> None:
        self.__game = game
    def run(self):
        self.__game.set_cursor_to_setting()

class ChangeSetting():
    """「せってい」にカーソルが合った状態から、設定を変更して保存、「せってい」にカーソルを戻す。
    """
    def __init__(self, game: MockGame) -> None:
        self.__game = game
    def run(self):
        self.__game.change_setting()

class Load():
    """「せってい」にカーソルが合った状態からロードし、メニューを開き「レポート」にカーソルを合わせる。
    """
    def __init__(self, game: MockGame) -> None:
        self.__game = game
    def run(self):
        self.__game.load()

class WriteReport():
    """「レポート」にカーソルが合った状態から、レポートを書き、「レポート」にカーソルを戻す。
    """
    def __init__(self, game: MockGame) -> None:
        self.__game = game
    def run(self):
        self.__game.write_report()

class TestExecute(unittest.TestCase):
    def test_execute(self):

        target_seeds: List[int] = [0xbeefface]
        tsv: Optional[int] = None
        advances_by_opening_items: Optional[int] = 17

        game = MockGame(tsv, advances_by_opening_items)
        operations = (
            TransitionToQuickBattle(game),
            GenerateNextTeamPair(game),
            EnterWaitAndExitQuickBattle(game),
            SetCursorToSetting(game),
            ChangeSetting(game),
            Load(game),
            WriteReport(game),
        )

        execute_automation(operations, target_seeds, tsv, advances_by_opening_items)
        print(game.result)
        self.assertEqual(target_seeds[0], game.seed)

if __name__ == "__main__":
    unittest.main()
