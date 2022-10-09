from datetime import timedelta
import math
import random
from typing import List, Optional

from lcg.gc import LCG
from xddb import generate_quick_battle
from xdrngtool import TeamPair, decode_quick_battle

class MockOperationReturnsTeamPair():
    """コンストラクタでいますぐバトル生成のリストを受け取り、runが呼ばれる度に先頭から返す。
    """
    def __init__(self, sequence: List[TeamPair]) -> None:
        self.__sequence = sequence
    def run(self):
        return self.__sequence.pop(0)

class MockOperation():
    """何もしない
    """
    def __init__(self) -> None:
        self.called = 0
    def run(self):
        self.called += 1

class MockCurrentSeedSearcher():
    """コンストラクタでseedのリストを受け取り、searchが呼ばれる度に先頭から返す。
    """
    def __init__(self, seeds: List[int]) -> None:
        self.__seeds = seeds
    def search(self) -> int:
        return self.__seeds.pop(0)

class MockGame():
    """ゲームを模す。
    """
    def __init__(self, tsv: Optional[int] = None, advances_by_opening_items: Optional[int] = None) -> None:
        self.__tsv = tsv
        self.__advances_by_opening_items = advances_by_opening_items
        self.__lcg = LCG(0)

        # 回数を数える
        self.__reset = 0
        self.__show_moltres = timedelta()
        self.__generate_quick_battle = 0
        self.__set_cursor_to_setting = False
        self.__change_setting = 0
        self.__load = False
        self.__write_report = 0

    def generate_quick_battle(self) -> TeamPair:
        ret, _ = decode_quick_battle(generate_quick_battle(self.__lcg, self.__tsv) if self.__tsv is not None else generate_quick_battle(self.__lcg))
        if self.__show_moltres != timedelta():
            self.__generate_quick_battle += 1
        return ret
    
    def show_moltres(self, td: timedelta):
        self.__lcg.adv(math.floor(3842 * td.total_seconds()))
        self.__show_moltres = td

    def set_cursor_to_setting(self):
        self.__set_cursor_to_setting = True

    def change_setting(self):
        self.__lcg.adv(40)
        self.__change_setting += 1
    
    def load(self):
        if self.__advances_by_opening_items is None:
            raise Exception("Attempted to load even though advances_by_opening_items is None.")
        self.__lcg.adv((self.__advances_by_opening_items - 1) * 2)
        self.__load = True

    def write_report(self):
        self.__lcg.adv(63)
        self.__write_report += 1

    def reset(self):
        self.__lcg = LCG(random.randint(0, 0xffffffff))
        self.__reset += 1
        self.__show_moltres = timedelta()
        self.__generate_quick_battle = 0
        self.__set_cursor_to_setting = False
        self.__change_setting = 0
        self.__load = False
        self.__write_report = 0
    
    @property
    def seed(self):
        return self.__lcg.seed

    @property
    def result(self):
        return {
            "reset": self.__reset,
            "show_moltres": f"{self.__show_moltres}",
            "generate_quick_battle": self.__generate_quick_battle,
            "set_cursor_to_setting": self.__set_cursor_to_setting,
            "change_setting": self.__change_setting,
            "load": self.__load,
            "write_report": self.__write_report,
        }
