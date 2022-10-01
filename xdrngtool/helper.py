from datetime import timedelta
from time import sleep
from typing import List, Optional, Tuple

from xddb import EnemyTeam

from .abc import XDRNGOperations
from .util import get_current_seed, get_wait_time, is_suitable_for_waiting, decide_route

def decide_target(
    operations: XDRNGOperations,
    target_seeds: List[int], 
    tsv: int, 
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
    tsv: int,
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
    tsv: int,
    advances_by_opening_items: Optional[int],
) -> None:
    """経路に従って消費します。

    Args:
        operations (XDRNGOperations): XDRNGOperations抽象クラスを継承したクラスのオブジェクト
        current_seed (int): 現在のseed
        target (Tuple[int, timedelta]): 目標seedと待機時間のタプル
        tsv (int): TSV
        advances_by_opening_items (Optional[int]): もちものを開く際の消費数
    """

    teams, change_setting_count, write_report_count, open_items_count, watch_steps_count = decide_route(current_seed, target[0], tsv, advances_by_opening_items)

    for team_pair in teams:
        # 色回避によって生成ルートが変更される
        # TSVを正しく指定しなかったなど
        if team_pair != operations.generate_next_team_pair():
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
    