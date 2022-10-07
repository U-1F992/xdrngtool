from datetime import timedelta
import math
from typing import List, Optional, Set, Tuple

from xddb import PlayerTeam, EnemyTeam, generate_quick_battle
from lcg.gc import LCG

from .constant import *
from .protocol import TeamPair

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
    index = LCG.get_index(seed=target_seed, init_seed=current_seed)
    sec = index / ADVANCES_PER_SECOND_BY_MOLTRES
    return timedelta(seconds=sec) - LEFTOVER_WAIT_TIME

def search_path(
    current_seed: int,
    target_seed: int,
    tsv: Optional[int] = None,
    advances_by_opening_items: Optional[int] = None
) -> Tuple[List[Tuple[TeamPair, int, Set[int]]], int, int]:
    """消費経路を算出します。

    Args:
        current_seed (int): 現在のseed
        target_seed (int): 目標のseed
        tsv (int, optional): TSV。正確に指定されない場合、実際のいますぐバトルの生成結果および回数は異なる可能性が生じます。 Defaults to None.
        advances_by_opening_items (Optional[int], optional): もちものを開く際の消費数。 Defaults to None.

    Returns:
        Tuple[List[Tuple[TeamPair, int, Set[int]]], int, int]: 消費経路\n
        （いますぐバトルの生成、生成前のseed、P1側手持ちのpsv）のタプルのリスト、設定変更回数、レポート回数
    """
    
    CANNOT_REACH_EXCEPTION = Exception(f"No way to reach {target_seed:X} from {current_seed:X}.")

    total_advances = LCG.get_index(seed=target_seed, init_seed=current_seed)
    lcg = LCG(current_seed)

    # 生成結果と残り消費数のペアのリスト
    sequence: List[Tuple[TeamPair, int]] = []
    
    while lcg.index_from(current_seed) <= total_advances:
        team_pair, _ = decode_quick_battle(generate_quick_battle(lcg, tsv))
        leftover = total_advances - lcg.index_from(current_seed)
        sequence.append((team_pair, leftover))
    sequence.pop()

    _teams: List[TeamPair] = []
    change_setting: int = 0
    write_report: int = 0

    if advances_by_opening_items is None:
        
        # advances_by_opening_itemsがNoneの場合 => ロードしない
        # 40で割り切れるようにいますぐバトルの生成を切り上げる。
        
        leftover = total_advances

        if len(sequence) == 0:
            # 1回も生成していないが、残りを40で割り切れない。
            if leftover % ADVANCES_BY_CHANGING_SETTING != 0:
                raise CANNOT_REACH_EXCEPTION

        else:
            can_finish: List[bool] = [item[1] % ADVANCES_BY_CHANGING_SETTING == 0 for item in sequence]
            try:
                last_index = len(can_finish) - can_finish[::-1].index(True) - 1
            except ValueError:
                # リストの中にTrueがない、どこで切り上げても40で割り切れない。
                raise CANNOT_REACH_EXCEPTION

            if last_index == 0:
                leftover = sequence[0][1]
                _teams = [item[0] for item in sequence]
            else:
                leftover = sequence[:last_index + 1][-1][1]
                _teams = [item[0] for item in sequence][:last_index + 1]

        change_setting = leftover // ADVANCES_BY_CHANGING_SETTING
        
    else:
        
        # advances_by_opening_itemsがNoneでない場合 => ロードする
        # 40a + by_loading + 63b で表す。
        
        advances_by_loading = (advances_by_opening_items - 1) * 2
        
        if len(sequence) == 0:
            leftover = total_advances - advances_by_loading
        else:
            # 残り消費数が63*40+by_loading以上になるまで生成を切り上げる
            while sequence[-1][1] < ADVANCES_BY_WRITING_REPORT * ADVANCES_BY_CHANGING_SETTING + advances_by_loading:
                sequence.pop()
            if len(sequence) == 0:
                leftover = total_advances - advances_by_loading
            else:
                leftover = sequence[-1][1] - advances_by_loading
        
        try:
            write_report, change_setting = _search_pair_with_the_smallest_sum(leftover)
        except:
            raise CANNOT_REACH_EXCEPTION
        _teams = [item[0] for item in sequence]
        
    # _teamsを詰め替える
    # 生成結果、生成"前"のseed、psv
    teams: List[Tuple[TeamPair, int, Set[int]]] = []
    _lcg = LCG(current_seed)
    for _ in _teams:
        seed_before = _lcg.seed
        team, psvs = decode_quick_battle(generate_quick_battle(_lcg, tsv))
        teams.append((team, seed_before, psvs))

    path = (teams, change_setting, write_report)
    return path

def decode_quick_battle(raw: Tuple[PlayerTeam, EnemyTeam, int, Set[int]]) -> Tuple[TeamPair, Set[int]]:
    """xddbから受け取る生データを、実際の生成結果に変換する

    Args:
        raw (Union[Tuple[PlayerTeam, EnemyTeam, int], Tuple[PlayerTeam, EnemyTeam, int, Set[int]]]): generate_quick_battleの結果

    Returns:
        TeamPair: 実際の生成結果
    """

    p_team, e_team, raw_hp, p_team_psvs = raw
    
    p1_base, p2_base = p_team.base_hp
    e1_base, e2_base = e_team.base_hp
    # https://github.com/yatsuna827/xddb/blob/dc619a3ec909a44f33ac5bd7df6dcc9e0e807977/src/xddb/client.py#L62
    hp = [
        e1_base + ((raw_hp >> 24) & 0xFF),
        e2_base + ((raw_hp >> 16) & 0xFF),
        p1_base + ((raw_hp >> 8) & 0xFF),
        p2_base + (raw_hp & 0xFF),
    ]

    p = (p_team, hp[2], hp[3])
    e = (e_team, hp[0], hp[1])
    
    return ((p, e), p_team_psvs)
    
def _search_pair_with_the_smallest_sum(total_advances: int) -> Tuple[int, int]:
    """total_advances消費するために必要な設定変更回数とレポート回数の組を返す。

    Args:
        total_advances (int): 2520以上の整数

    Returns:
        Tuple[int, int]: 設定変更回数とレポート回数の組
    
    ---
    `63*x+40*y=z`（`63*40<=z`の整数）を満たす`(x,y)`（`x`,`y`はそれぞれ0以上の整数）について、`x+y`が最小となるものを考える。

    `63*x+40*y=z`は、`z`の値に関わらず整数解を持つ（証明省略）。
    https://examist.jp/mathematics/integer/axby-kouzou/
    
    `63*x+40*y=1`の特殊解は`(7,-11)`より、`63*x+40*y=z`の特殊解は`(7*z,-11*z)`、
    したがって一般解は、任意の整数を`t`とおいて`(40*t+7*z,-63*t-11*z)`。

    `0<=x`かつ`0<=y`より、`t`の範囲は`-7*z/40<=t<=-11*z/63`

    `x+y=-23*t-4*z`は単調減少するので、
    `x+y`が最小となる`t`は`floor(-11*z/63)`
    """

    if total_advances < 2520:
        # 2520未満の場合は全探索する。
        # 見つからない場合はException
        return _search_pair_with_the_smallest_sum_under_2520(total_advances)

    t = math.floor(-11 * total_advances / 63)
    return (40 * t + 7 * total_advances, -63 * t - 11 * total_advances)

def _search_pair_with_the_smallest_sum_under_2520(total_advances: int) -> Tuple[int, int]:
    """total_advances消費するために必要な設定変更回数とレポート回数の組を全探索で探す。。

    Args:
        total_advances (int): _description_

    Raises:
        Exception: _description_

    Returns:
        Tuple[int, int]: _description_
    """
    pairs: List[Tuple[int, int]] = []
    for x in range(total_advances // 63 + 1):
        for y in range(total_advances // 40 + 1):
            if 63 * x + 40 * y == total_advances:
                pairs.append((x, y))
    if len(pairs) == 0:
        raise Exception("The specified number cannot be combined in 64 and 40.")
    return sorted(pairs, key=lambda p: p[0] + p[1]).pop(0)
