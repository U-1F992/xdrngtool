from datetime import timedelta
import unittest

from xdrngtool import TeamPair, execute_automation

from mocks import MockGame


class TransitionToQuickBattle():
    def __init__(self, game: MockGame) -> None:
        self.__game = game
    def run(self):
        #print("\n----------------------------------------\n")
        self.__game.reset()

class GenerateNextTeamPair():
    def __init__(self, game: MockGame) -> None:
        self.__game = game
    def run(self) -> TeamPair:
        ret = self.__game.generate_quick_battle()
        #print(ret)
        return ret

class EnterWaitAndExitQuickBattle():
    def __init__(self, game: MockGame) -> None:
        self.__game = game
    def run(self, td: timedelta):
        self.__game.show_moltres(td)
        #print("~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ")

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

        # 目標seed、指定TSV、実際のTSV、もちもの消費（ロードの有無）
        test_case = [
            # TSV未指定、ロードなし
            ([0xbeefface], None, 0, None),
            # TSV未指定で色回避あり、ロードなし
            ([0xbeefface], None, 3257, None),
            # TSVを適切に指定、ロードなし
            ([0xbeefface], 0, 0, None),
            # 誤ったTSVを指定、色回避あり、ロードなし
            ([0xbeefface], 0, 3257, None),

            # TSV未指定、ロードあり
            ([0xbeefface], None, 0, 17),
            # TSV未指定で色回避あり、ロードあり
            ([0xbeefface], None, 3257, 17),
            # TSVを適切に指定、ロードあり
            ([0xbeefface], 0, 0, 17),
            # 誤ったTSVを指定、色回避あり、ロードあり
            ([0xbeefface], 0, 3257, 17),
        ]
        for target_seeds, tsv, game_tsv, advances_by_opening_items in test_case:
            
            with self.subTest():

                game = MockGame(game_tsv, advances_by_opening_items)
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
