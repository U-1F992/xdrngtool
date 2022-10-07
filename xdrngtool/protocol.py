from datetime import timedelta
from typing import List, Tuple #, Protocol # 3.8+
from typing_extensions import Protocol # ~3.7
from xddb import EnemyTeam, PlayerTeam

# いますぐバトルの生成結果を表すTypeAlias
TeamPair = Tuple[Tuple[PlayerTeam, int, int], Tuple[EnemyTeam, int, int]]

class Operation(Protocol):
    """引数・戻り値なしのrunメソッドを持つクラスを表現し、静的ダックタイピングをサポートする。
    """
    def run(self):
        pass

class OperationReturnsTeamPair(Protocol):
    """引数なし・戻り値TeamPairのrunメソッドを持つクラスを表現し、静的ダックタイピングをサポートする。
    """
    def run(self) -> TeamPair:
        return (PlayerTeam.Mewtwo, 100, 100), (EnemyTeam.Articuno, 100, 100)

class OperationTakesTimedelta(Protocol):
    """引数timedelta・戻り値なしのrunメソッドを持つクラスを表現し、静的ダックタイピングをサポートする。
    """
    def run(self, td: timedelta):
        pass

class ITargetSelector(Protocol):
    def execute(self, target_seeds: List[int]) -> Tuple[int, Tuple[int, timedelta]]:
        return 0, (0, timedelta())

class ICurrentSeedSearcher(Protocol):
    def search(self) -> int:
        return 0

class ISeedAdjuster(Protocol):
    def execute(self, target: Tuple[int, timedelta]) -> None:
        pass
