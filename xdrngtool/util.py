from datetime import timedelta
import math
from typing import Callable, List, Optional, Tuple

from xddb import PlayerTeam, EnemyTeam, generate_quick_battle, XDDBClient
from lcg.gc import LCG
from .constant import *

TeamPair = Tuple[Tuple[PlayerTeam, int, int], Tuple[EnemyTeam, int, int]]

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

def decide_route(
    current_seed: int,
    target_seed: int,
    tsv: int = DEFAULT_TSV,
    opts: Optional[Tuple[int, int]] = None
) -> Tuple[List[TeamPair], int, int, int, int]:
    """消費経路を算出します。

    Args:
        current_seed (int): 現在のseed
        target_seed (int): 目標のseed
        tsv (int, optional): TSV。正確に指定されない場合、実際のいますぐバトルの生成結果および回数は異なる可能性が生じます。 Defaults to DEFAULT_TSV.
        opts (Optional[Tuple[int, int]], optional): ロード後に使用する消費数（ロード時の強制消費数、もちものを開く際の消費数）。 Defaults to None.

    Returns:
        Tuple[List[TeamPair], int, int, int, int]: 消費経路（いますぐバトルの生成リスト、設定変更回数、レポート回数、もちものを開く回数、腰振りを見る回数）
    """
    
    CANNOT_REACH_ERROR = Exception(f"No way to reach {target_seed:X} from {current_seed:X}.")

    total_advances = LCG(target_seed).index_from(current_seed)
    lcg = LCG(current_seed)

    # 生成結果と残り消費数のペアのリスト
    sequence: List[Tuple[TeamPair, int]] = []
    
    while lcg.index_from(current_seed) <= total_advances:
        team_pair = decode_quick_battle(generate_quick_battle(lcg, tsv))
        leftover = total_advances - lcg.index_from(current_seed)
        sequence.append((team_pair, leftover))
    sequence.pop()

    teams: List[TeamPair] = []
    change_setting: int = 0
    write_report: int = 0
    open_items: int = 0
    watch_steps: int = 0

    if opts is None:
        
        # optsがNoneの場合 => ロードしない
        # 40で割り切れるようにいますぐバトルの生成を切り上げる。
        
        leftover = total_advances

        if len(sequence) == 0:
            if leftover % ADVANCES_BY_CHANGING_SETTING != 0:
                raise CANNOT_REACH_ERROR

        else:
            can_finish: List[bool] = [item[1] % ADVANCES_BY_CHANGING_SETTING == 0 for item in sequence]
            try:
                last_index = len(can_finish) - can_finish[::-1].index(True) - 1
            except ValueError:
                raise CANNOT_REACH_ERROR

            if last_index == 0:
                leftover = sequence[0][1]
                teams = [item[0] for item in sequence]
            else:
                leftover = sequence[:last_index + 1][-1][1]
                teams = [item[0] for item in sequence][:last_index + 1]

        change_setting = math.floor(leftover / ADVANCES_BY_CHANGING_SETTING)
        
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
        teams = [item[0] for item in sequence]

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
    
    route = (teams, change_setting, write_report, open_items, watch_steps)
    test_route(route, current_seed, target_seed, tsv, opts) # あまり自信がないのでチェック
    return route

def test_route(
    route: Tuple[List[TeamPair], int, int, int, int],
    current_seed: int,
    target_seed: int,
    tsv: int,
    opts: Optional[Tuple[int, int]]
) -> None:
    
    teams, change_setting, write_report, open_items, watch_steps = route
    advances_by_loading, advances_by_opening_items = opts if opts is not None else (0, 0)

    test_lcg = LCG(current_seed)
    for i in teams:
        generate_quick_battle(test_lcg, tsv)
    test_lcg.adv(change_setting * ADVANCES_BY_CHANGING_SETTING)
    test_lcg.adv(advances_by_loading)
    test_lcg.adv(write_report * ADVANCES_BY_WRITING_REPORT)
    test_lcg.adv(open_items * advances_by_opening_items)
    test_lcg.adv(watch_steps * ADVANCES_BY_WATCHING_STEPS)
    if test_lcg.seed != target_seed:
        raise Exception(f"Corner case has been found. Please report to the developer: \ncurrent_seed={current_seed:X}\ntarget_seed={target_seed:X}\ntsv={tsv}\nopts={opts}\nresult={(len(teams), change_setting, write_report, open_items, watch_steps)}\nactual={test_lcg.seed:X}")

def decode_quick_battle(raw: Tuple[int, int, int]) -> TeamPair:
    """xddbから受け取る生データを、実際の生成結果に変換する

    Args:
        raw (Tuple[int, int, int]): generate_quick_battleの結果

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
    return not is_even(value)

def get_current_seed(generate_next_team_pair: Callable[[], TeamPair], tsv: int = DEFAULT_TSV) -> int:
    """現在のseedを取得します。

    コールバックの実装については、あらかじめいますぐバトル生成済み画面まで誘導しておき、B,A入力で再生成して画像認識しreturnすることを想定しています。

    Args:
        generate_next_team_pair (Callable[[], TeamPair]): いますぐバトルの生成結果を返すコールバック。
        tsv (int, optional):TSV。正確に指定されない場合、実際のいますぐバトルの生成結果および回数は異なる可能性が生じます。 Defaults to DEFAULT_TSV.

    Raises:
        Exception: コールバックが例外で停止した場合に発生します。誤操作などで回復不能（リセット）に陥った際に利用できます。

    Returns:
        int: 現在のseed
    """
    
    client = XDDBClient()
    
    try:
        first = generate_next_team_pair()
        second = generate_next_team_pair()
    except:
        raise

    search_result = client.search(first[0], first[1], second[0], second[1])
    length = len(search_result)

    if length == 1:
        # 検索結果が1件の場合
        return search_result.pop()

    elif length == 0:
        # 検索結果が0件の場合
        # 2回取得からやり直す
        try:
            return get_current_seed(generate_next_team_pair, tsv)
        except:
            raise
    
    else:
        # 検索結果が2件以上の場合
        # それぞれのseedからパーティ生成し、実際の生成結果と比較する
        next: set[int] = set()
        while True:
            third = generate_next_team_pair()
            for seed in search_result:
                lcg = LCG(seed)
                raw = generate_quick_battle(lcg, tsv)
                generate_result = decode_quick_battle(raw)
                
                if generate_result == third:
                    next.add(lcg.seed)
            
            if len(next) > 1:
                # それぞれから生成して、一致するものが複数件あった場合
                # 生成先seedからさらに生成して比較する
                search_result = next.copy()
                next.clear()
            else:
                break;    
        
        if len(next) == 0:
            # 0件になった場合
            # 2回取得からやり直す
            try:
                return get_current_seed(generate_next_team_pair, tsv)
            except:
                raise
        
        return next.pop()
