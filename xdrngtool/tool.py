from datetime import timedelta
from time import sleep
from typing import List, Optional, Tuple

from xddb import EnemyTeam, generate_quick_battle
from lcg.gc import LCG

from .abc import XDRNGOperations
from .util import decide_route, decode_quick_battle, get_current_seed, get_wait_time, is_suitable_for_waiting

def execute_operation(
    operations: XDRNGOperations, 
    target_seeds: List[int], 
    tsv: Optional[int] = None, 
    advances_by_opening_items: Optional[int] = None, 
) -> bool:
    """ポケモンXDの乱数調整を行います。

    Args:
        operations (XDRNGOperations): XDRNGOperations抽象クラスを継承したクラスのオブジェクト
        target_seeds (List[int]): 目標seedのリスト
        tsv (int): TSV。指定しない場合、いますぐバトルの生成結果に齟齬が生じ再計算が発生する可能性があります。 Defaults to None.
        advances_by_opening_items (Optional[int]): もちものを開く際の消費数。 Defaults to None.

    Returns:
        bool: 試行の成否
    """
    
    current_seed, target = decide_target(operations, target_seeds, tsv)
    
    try:
        current_seed = advance_by_moltres(operations, target, tsv)
        advance_according_to_route(current_seed, target, tsv, advances_by_opening_items)
    except:
        return execute_operation(operations, target_seeds, tsv, advances_by_opening_items)
    
    return operations.verify()

def decide_target(
    operations: XDRNGOperations,
    target_seeds: List[int], 
    tsv: Optional[int], 
) -> Tuple[int, Tuple[int, timedelta]]:
    """初期seed厳選を行い、目標seedを決定します。

    Args:
        operations (XDRNGOperations): XDRNGOperations抽象クラスを継承したクラスのオブジェクト
        target_seeds (List[int]): 目標seedのリスト
        tsv (int): TSV

    Returns:
        Tuple[int, Tuple[int, timedelta]]: 目標seedと待機時間のタプル
    """

    current_seed: int = int()
    target: Tuple[int, timedelta] = (int(), timedelta())

    while True:
        operations.transition_to_quick_battle()
        try:
            current_seed = get_current_seed(operations, tsv)
        except:
            continue
        
        target = sorted(
            [(target_seed, get_wait_time(current_seed, target_seed)) for target_seed in target_seeds]
        )[0]
        
        if is_suitable_for_waiting(target[1]):
            break
    return current_seed, target

def advance_by_moltres(
    operations: XDRNGOperations,
    target: Tuple[int, timedelta],
    tsv: Optional[int],
) -> int:
    """いますぐバトルにファイヤーを出し、大量消費します。

    Args:
        operations (XDRNGOperations): XDRNGOperations抽象クラスを継承したクラスのオブジェクト
        target (Tuple[int, timedelta]): 目標seedと待機時間のタプル
        tsv (int): TSV

    Raises:
        Exception: リセットが必要です。

    Returns:
        int: 大量消費後の現在のseed
    """

    # いますぐバトル生成済み画面から
    # 1. ファイヤーが出るまで再生成
    # 2. 戦闘に入りwait_time待機
    # 3. 戦闘から出て再度現在のseedを特定

    while True:
        team_pair = operations.generate_next_team_pair()
        if team_pair[1][0] == EnemyTeam.Moltres:
            break

    operations.enter_quick_battle()
    sleep(target[1].total_seconds())
    operations.exit_quick_battle()
    
    current_seed = get_current_seed(operations, tsv)
    
    # 待機時間が消費前の待機時間より長いことで、消費しすぎたことを判定
    waited_too_long = get_wait_time(current_seed, target[0]) > target[1]
    if waited_too_long:
        raise Exception("Waited too long.")

    return current_seed

def advance_according_to_route(
    operations: XDRNGOperations,
    current_seed: int,
    target: Tuple[int, timedelta],
    tsv: Optional[int],
    advances_by_opening_items: Optional[int],
) -> None:
    """経路を導出し、それに従って消費します。

    Args:
        operations (XDRNGOperations): XDRNGOperations抽象クラスを継承したクラスのオブジェクト
        current_seed (int): 現在のseed
        target (Tuple[int, timedelta]): 目標seedと待機時間のタプル
        tsv (int): TSV
        advances_by_opening_items (Optional[int]): もちものを開く際の消費数
    """

    teams, change_setting_count, write_report_count, open_items_count, watch_steps_count = decide_route(current_seed, target[0], tsv, advances_by_opening_items)

    for team_seed_psvs in teams:
        
        team_expected, seed_before, psvs = team_seed_psvs
        team_generated = operations.generate_next_team_pair()

        # 生成結果と予測が異なる場合、色回避によって生成ルートが変更される（TSVを指定しなかった、指定したTSVが誤っていたなど）
        # - psvをtsvに設定して一致するものがあれば、そこから復帰
        # - psvのいずれをtsvに設定しても一致するものがなければ、現在seedを再特定して復帰
        
        if team_generated != team_expected:

            for tsv_suggested in psvs:
                _lcg = LCG(seed_before)
                team_suggested, _ = decode_quick_battle(generate_quick_battle(_lcg, tsv_suggested))
                if team_generated == team_suggested:
                    advance_according_to_route(operations, _lcg.seed, target, tsv, advances_by_opening_items)
                    return

            conflict_current_seed = get_current_seed(operations, tsv)
            advance_according_to_route(operations, conflict_current_seed, target, tsv, advances_by_opening_items)
            return
    
    operations.set_cursor_to_setting()
    for _ in range(change_setting_count):
        operations.change_setting()
    
    if advances_by_opening_items is None:
        return

    operations.load()
    for _ in range(write_report_count):
        operations.write_report()
    operations.set_cursor_to_items()
    for _ in range(open_items_count):
        operations.open_items()
    for _ in range(watch_steps_count):
        operations.watch_steps()
    