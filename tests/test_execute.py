from datetime import timedelta
from typing import List, Optional
import unittest

from xdrngtool import TeamPair, execute_automation, title_logo

from mocks import MockGame


class TransitionToQuickBattle():
    def __init__(self, game: MockGame) -> None:
        self.__game = game
    def run(self):
        print("\n----------------------------------------\n")
        self.__game.reset()

class GenerateNextTeamPair():
    def __init__(self, game: MockGame) -> None:
        self.__game = game
    def run(self) -> TeamPair:
        ret = self.__game.generate_quick_battle()
        print(ret)
        return ret

class EnterWaitAndExitQuickBattle():
    def __init__(self, game: MockGame) -> None:
        self.__game = game
    def run(self, td: timedelta):
        self.__game.show_moltres(td)
        print("~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ")

class SetCursorToSetting():
    def __init__(self, game: MockGame) -> None:
        self.__game = game
    def run(self):
        self.__game.set_cursor_to_setting()

class ChangeSetting():
    def __init__(self, game: MockGame) -> None:
        self.__game = game
    def run(self):
        self.__game.change_setting()

class Load():
    def __init__(self, game: MockGame) -> None:
        self.__game = game
    def run(self):
        self.__game.load()

class WriteReport():
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

        print(title_logo)

if __name__ == "__main__":
    unittest.main()
