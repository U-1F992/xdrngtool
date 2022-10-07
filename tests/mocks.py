from typing import List

from xdrngtool import TeamPair

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
