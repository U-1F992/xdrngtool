from datetime import timedelta
from typing import List, Optional, Tuple, TypeAlias

from xddb import PlayerTeam, EnemyTeam, generate_quick_battle
from lcg import LCG

TeamPair: TypeAlias = Tuple[Tuple[PlayerTeam, int, int], Tuple[EnemyTeam, int, int]]

# 最短の待機時間
# 戦闘にファイヤーが登場するまで、および降参してから消費が止まるまでにはラグがあるため、短すぎると制御が難しいです。
MINIMUM_WAIT_TIME = timedelta(minutes=1)

# 最長の待機時間
# 待機が長すぎると初期seed厳選をする意味がないですが、短く設定し過ぎると厳選に時間がかかりすぎます。
# 経験上3時間ぐらいがいい塩梅です。
MAXIMUM_WAIT_TIME = timedelta(hours=3)

# 待機時間から切り上げる時間
# 短い方が戦闘後の消費行動を少なくできますが、先述の理由で短くし過ぎると消費しすぎるなどの不具合が発生します。
LEFTOVER = timedelta(minutes=1)

# いますぐバトルにファイヤーを出した場合の消費数/秒
# 一般的には3713.6と言われていますが（出典不明）、3842程度で上手くいきます。
ADVANCES_PER_SECOND_BY_MOLTRES = 3842

ADVANCES_BY_CHANGE_SETTING = 40
ADVANCES_BY_WRITE_REPORT = 63
ADVANCES_BY_WATCHING_STEPS = 2

def get_wait_time(
    current_seed: int,
    target_seed: int,
) -> timedelta:
    """いますぐバトルにファイヤーを出した場合の、seed間の待機時間を算出します。

    Args:
        current_seed (int): 現在のseed
        target_seed (int): 目標のseed

    Returns:
        timedelta: 待機時間
    """
    sec = LCG(target_seed).index_from(current_seed) / ADVANCES_PER_SECOND_BY_MOLTRES
    return timedelta(seconds=sec) - LEFTOVER

def is_short_enough(wait_time: timedelta) -> bool:
    """待機時間が待機に適しているか判定します。

    Args:
        wait_time (timedelta): 待機時間

    Returns:
        bool: 待機に適しているか
    """
    return MINIMUM_WAIT_TIME < wait_time and wait_time < MAXIMUM_WAIT_TIME

def get_route(
    current_seed: int,
    target_seed: int,
    tsv: int = 0x10000,
    opts: Optional[Tuple[int, int]] = None
) -> Tuple[List[TeamPair], int, int, int, int]:
    """消費経路を算出します。

    Args:
        current_seed (int): 現在のseed
        target_seed (int): 目標のseed
        tsv (int, optional): TSV。正確に指定されない場合、実際のいますぐバトルの生成結果および回数は異なる可能性が生じます。 Defaults to 0x10000.
        opts (Optional[Tuple[int, int]], optional): ロード後の使用する消費数（ロード時の強制消費数、もちものを開く際の消費数）。 Defaults to None.

    Returns:
        Tuple[List[TeamPair], int, int, int, int]: 消費経路（いますぐバトルの生成リスト、設定変更回数、レポート回数、もちものを開く回数、腰振りを見る回数）
    """

    # optsがNoneの場合（ロードしない）
    # 40で割り切れるようにいますぐバトルの生成を切り上げる。

    # optsがNoneでない場合（ロードする）
    # 40a + by_loading + 63b + by_opening_items*c + 2d で表す。
    
    lcg = LCG(current_seed)
    result = generate_quick_battle(lcg, tsv)

    return ([(PlayerTeam.Mewtwo, 100, 100), (EnemyTeam.Articuno, 100, 100)], 0, 0, 0, 0)
