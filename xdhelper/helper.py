from asyncore import write
from datetime import timedelta
import math
from typing import Optional, TypeAlias

from xddb import PlayerTeam, EnemyTeam, generate_quick_battle
from .lcg import LCG
from .base_hp import PLAYER_BASE_HP, ENEMY_BASE_HP

TeamPair: TypeAlias = tuple[tuple[PlayerTeam, int, int], tuple[EnemyTeam, int, int]]

# 最短の待機時間
# 戦闘にファイヤーが登場するまで、および降参してから消費が止まるまでにはラグがあるため、短すぎると制御が難しいです。
MINIMUM_WAIT_TIME = timedelta(minutes=1)

# 最長の待機時間
# 待機が長すぎると初期seed厳選をする意味がないですが、短く設定し過ぎると厳選に時間がかかりすぎます。
# 経験上3時間ぐらいがいい塩梅です。
MAXIMUM_WAIT_TIME = timedelta(hours=3)

# 待機時間から天引きする時間
# 短い方が戦闘後の消費行動を少なくできますが、先述の理由で短くし過ぎると消費しすぎるなどの不具合が発生します。
LEFTOVER_WAIT_TIME = timedelta(minutes=1)

# いますぐバトルにファイヤーを出した場合の消費数/秒
# 一般的には3713.6と言われていますが（出典不明）、3842程度で上手くいきます。
ADVANCES_PER_SECOND_BY_MOLTRES = 3842

# 振動設定変更の消費数
ADVANCES_BY_CHANGING_SETTING = 40
# レポートにかかる消費数
ADVANCES_BY_WRITING_REPORT = 63
# 主人公の腰振りにかかる消費数
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
    index = LCG(target_seed).index_from(current_seed)
    sec = index / ADVANCES_PER_SECOND_BY_MOLTRES
    return timedelta(seconds=sec) - LEFTOVER_WAIT_TIME

def is_suitable_for_waiting(wait_time: timedelta) -> bool:
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
    opts: Optional[tuple[int, int]] = None
) -> tuple[list[TeamPair], int, int, int, int]:
    """消費経路を算出します。

    Args:
        current_seed (int): 現在のseed
        target_seed (int): 目標のseed
        tsv (int, optional): TSV。正確に指定されない場合、実際のいますぐバトルの生成結果および回数は異なる可能性が生じます。 Defaults to 0x10000.
        opts (Optional[tuple[int, int]], optional): ロード後の使用する消費数（ロード時の強制消費数、もちものを開く際の消費数）。 Defaults to None.

    Returns:
        tuple[list[TeamPair], int, int, int, int]: 消費経路（いますぐバトルの生成リスト、設定変更回数、レポート回数、もちものを開く回数、腰振りを見る回数）
    """

    CANNOT_REACH_ERROR = Exception(f"No way to reach {target_seed:X} from {current_seed:X}.")

    total_advances = LCG(target_seed).index_from(current_seed)
    lcg = LCG(current_seed)

    # 生成結果と残り消費数のペアのリスト
    sequence: list[tuple[TeamPair, int]] = []
    
    while lcg.index_from(current_seed) <= total_advances:
        team_pair = decode(generate_quick_battle(lcg, tsv))
        leftover = total_advances - lcg.index_from(current_seed)
        sequence.append((team_pair, leftover))
    sequence.pop()

    if opts is None:
        
        # optsがNoneの場合 => ロードしない
        # 40で割り切れるようにいますぐバトルの生成を切り上げる。
        
        leftover = total_advances
        teams: list[TeamPair] = []
        change_setting: int = 0

        if len(sequence) == 0:
            if leftover % ADVANCES_BY_CHANGING_SETTING != 0:
                raise CANNOT_REACH_ERROR

        else:
            can_finish: list[bool] = [item[1] % ADVANCES_BY_CHANGING_SETTING == 0 for item in sequence]
            try:
                last_index = len(can_finish) - can_finish[::-1].index(True) - 1
            except ValueError:
                raise CANNOT_REACH_ERROR

            if last_index == 0:
                leftover = sequence[0][1]
                teams = [item[0] for item in sequence]
            else:
                leftover = sequence[:last_index + 1][1]
                teams = [item[0] for item in sequence][:last_index + 1]

        change_setting = math.floor(leftover / ADVANCES_BY_CHANGING_SETTING)
        
        return (teams, change_setting, 0, 0, 0)
        
    else:
        
        # optsがNoneでない場合 => ロードする
        # 40a + by_loading + 63b + by_opening_items*c + 2d で表す。
        
        advances_by_loading, advances_by_opening_items = opts
        leftover = total_advances
        if len(sequence) == 0:
            leftover -= advances_by_loading
        else:
            leftover = sequence[-1][1] - advances_by_loading
        
        # - もちもの消費が偶数であり残り消費数がADVANCES_BY_WRITE_REPORT=63より少ない奇数である場合、ADVANCES_BY_WRITE_REPORTより小さい奇数は消費できない
        # - もちもの消費が奇数だが、残り消費数がもちもの消費より少ない場合、もちもの消費より小さい奇数は消費できない
        # ため、いますぐバトルの生成を減らして残り消費数を増やす必要がある
        while (is_even(advances_by_opening_items) and leftover < ADVANCES_BY_WRITING_REPORT and is_odd(leftover)) or (is_odd(advances_by_opening_items) and leftover < advances_by_opening_items):
            try:
                sequence.pop()
            except IndexError:
                raise CANNOT_REACH_ERROR
            leftover = sequence[-1][1] - advances_by_loading

        # レポート回数
        # もちもの消費が偶数である場合、奇数の消費手段はレポートのみになるため
        # - 残り消費数が奇数である場合、レポート回数は奇数である
        # - 残り消費数が偶数である場合、偶数である
        write_report = math.floor(leftover / ADVANCES_BY_WRITING_REPORT)
        if (is_odd(leftover) and is_even(write_report)) or (is_even(leftover) and is_odd(write_report)):
            write_report = write_report - 1 if write_report != 0 else 0
        leftover -= ADVANCES_BY_WRITING_REPORT * write_report

        # 設定変更回数
        change_setting = math.floor(leftover / 40)
        leftover -= ADVANCES_BY_CHANGING_SETTING * change_setting
        
        # もちものを開く回数
        # - 残り消費数が奇数である場合、もちものを開く回数は奇数である
        # - 残り消費数が偶数である場合、偶数である
        open_items = math.floor(leftover / advances_by_opening_items)
        if (is_odd(leftover) and is_even(open_items)) or (is_even(leftover) and is_odd(open_items)):
            open_items = open_items - 1 if open_items != 0 else 0
        leftover -= advances_by_opening_items * open_items

        # 腰振り回数
        watch_steps = math.floor(leftover / ADVANCES_BY_WATCHING_STEPS)

        teams = [item[0] for item in sequence]
        return (teams, change_setting, write_report, open_items, watch_steps)

def decode(raw: tuple[int, int, int]) -> TeamPair:
    """xddbから受け取る生データを、実際の生成結果に変換する

    Args:
        raw (tuple[int, int, int]): generate_quick_battleの結果

    Returns:
        TeamPair: 実際の生成結果
    """

    raw_p_team, raw_e_team, raw_hp = raw

    p_team = PlayerTeam(raw_p_team)
    e_team = EnemyTeam(raw_e_team)
    
    p1_base, p2_base = PLAYER_BASE_HP[raw_p_team]
    e1_base, e2_base = ENEMY_BASE_HP[raw_e_team]
    # https://github.com/yatsuna827/xddb/blob/dc619a3ec909a44f33ac5bd7df6dcc9e0e807977/src/xddb/client.py#L62
    hp = [
        e1_base + ((raw_hp >> 24) & 0xFF),
        e2_base + ((raw_hp >> 16) & 0xFF),
        p1_base + ((raw_hp >> 8) & 0xFF),
        p2_base + (raw_hp & 0xFF),
    ]

    p = (p_team, hp[2], hp[3])
    e = (e_team, hp[0], hp[1])
    
    return (p, e)

def is_even(value: int) -> bool:
    return value % 2 == 0
def is_odd(value: int) -> bool:
    return value % 2 == 1
