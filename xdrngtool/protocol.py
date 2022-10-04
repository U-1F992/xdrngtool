from typing import Generic, Protocol, Tuple, TypeVar

from xddb import EnemyTeam, PlayerTeam

# いますぐバトルの生成結果を表すTypeAlias
TeamPair = Tuple[Tuple[PlayerTeam, int, int], Tuple[EnemyTeam, int, int]]

T = TypeVar("T")
class Operation(Protocol, Generic[T]):
    """「操作を実装するクラスは、引数なし、型Tを戻り値とするrunメソッドを持つ」ことを表現し、静的ダックタイピングをサポートする。
    """
    def run() -> T:
        pass
