from datetime import timedelta
from typing import Set, Tuple

from xddb import PlayerTeam, EnemyTeam
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
