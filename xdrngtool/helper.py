from datetime import timedelta
from time import sleep
from typing import Callable, List, Optional, Tuple

from xddb import EnemyTeam

from .util import TeamPair, get_current_seed, get_wait_time, is_suitable_for_waiting, decide_route

def decide_target(
    target_seeds: List[int], 
    tsv: int, 
    transition_to_quick_battle: Callable[[], None], 
    generate_next_team_pair: Callable[[], TeamPair]
) -> Tuple[int, Tuple[int, timedelta]]:
    """初期seed厳選を行い、目標seedを決定します。

    Args:
        target_seeds (List[int]): 目標seedのリスト
        tsv (int): TSV
        transition_to_quick_battle (Callable[[], None]): リセットし、1回いますぐバトルを生成した画面まで誘導するコールバック関数
        generate_next_team_pair (Callable[[], TeamPair]): 現在のいますぐバトル生成結果を破棄し、再度生成して渡すコールバック関数

    Returns:
        Tuple[int, Tuple[int, timedelta]]: 目標seedと待機時間のタプル
    """

    current_seed: int = int()
    target: Tuple[int, timedelta] = (int(), timedelta())

    while True:
        transition_to_quick_battle()
        try:
            current_seed = get_current_seed(generate_next_team_pair, tsv)
        except:
            continue
        
        target = sorted(
            [(target_seed, get_wait_time(current_seed, target_seed)) for target_seed in target_seeds]
        )[0]
        
        if is_suitable_for_waiting(target[1]):
            break
    return current_seed, target

def advance_by_moltres(
    target: Tuple[int, timedelta],
    tsv: int,
    generate_next_team_pair: Callable[[], TeamPair],
    enter_quick_battle: Callable[[], None], 
    exit_quick_battle: Callable[[], None], 
) -> int:
    """いますぐバトルにファイヤーを出し、大量消費します。

    Args:
        target (Tuple[int, timedelta]): 目標seedと待機時間のタプル
        tsv (int): TSV
        generate_next_team_pair (Callable[[], TeamPair]): 現在のいますぐバトル生成結果を破棄し、再度生成して渡すコールバック関数
        enter_quick_battle (Callable[[], None]): いますぐバトルを開始するコールバック関数
        exit_quick_battle (Callable[[], None]): いますぐバトルを降参し、1回いますぐバトルを生成するコールバック関数

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
        team_pair = generate_next_team_pair()
        if team_pair[1][0] == EnemyTeam.Moltres:
            break

    enter_quick_battle()
    sleep(target[1].total_seconds())
    exit_quick_battle()
    
    current_seed = get_current_seed(generate_next_team_pair, tsv)
    
    # 待機時間が消費前の待機時間より長いことで、消費しすぎたことを判定
    waited_too_long = get_wait_time(current_seed, target[0]) > target[1]
    if waited_too_long:
        raise Exception("Waited too long.")

    return current_seed

def advance_according_to_route(
    current_seed: int,
    target: Tuple[int, timedelta],
    tsv: int,
    advances_by_opening_items: Optional[int],
    generate_next_team_pair: Callable[[], TeamPair],
    set_cursor_to_setting: Callable[[], None],
    change_setting: Callable[[], None],
    load: Callable[[], None],
    write_report: Callable[[], None],
    set_cursor_to_items: Callable[[], None],
    open_items: Callable[[], None],
    watch_steps: Callable[[], None]
) -> None:
    """経路に従って消費します。

    Args:
        current_seed (int): 現在のseed
        target (Tuple[int, timedelta]): 目標seedと待機時間のタプル
        tsv (int): TSV
        advances_by_opening_items (Optional[int]): もちものを開く際の消費数
        generate_next_team_pair (Callable[[], TeamPair]): 現在のいますぐバトル生成結果を破棄し、再度生成して渡すコールバック関数
        set_cursor_to_setting (Callable[[], None]): いますぐバトル生成済み画面から、「せってい」にカーソルを合わせるコールバック関数
        change_setting (Callable[[], None]): 「せってい」にカーソルが合った状態から、設定を変更して保存、「せってい」にカーソルを戻すコールバック関数
        load (Callable[[], None]): 「せってい」にカーソルが合った状態からロードし、メニューを開き「レポート」にカーソルを合わせるコールバック関数
        write_report (Callable[[], None]): 「レポート」にカーソルが合った状態から、レポートを書き、「レポート」にカーソルを戻すコールバック関数
        set_cursor_to_items (Callable[[], None]): 「レポート」にカーソルが合った状態から、「もちもの」にカーソルを合わせるコールバック関数
        open_items (Callable[[], None]): 「もちもの」にカーソルが合った状態から、もちものを開いて閉じるコールバック関数
        watch_steps (Callable[[], None]): メニューが開いている状態から、メニューを閉じ腰振り1回分待機し、メニューを開くコールバック関数
    """

    teams, change_setting_count, write_report_count, open_items_count, watch_steps_count = decide_route(current_seed, target[0], tsv, advances_by_opening_items)

    for team_pair in teams:
        # 色回避によって生成ルートが変更される
        # TSVを正しく指定しなかったなど
        if team_pair != generate_next_team_pair():
            conflict_current_seed = get_current_seed(generate_next_team_pair, tsv)
            advance_according_to_route(conflict_current_seed, target, tsv, advances_by_opening_items, generate_next_team_pair, set_cursor_to_setting, change_setting, load, write_report, set_cursor_to_items, open_items, watch_steps)
            return
    
    set_cursor_to_setting()
    for i in range(change_setting_count):
        change_setting()
    
    if advances_by_opening_items is None:
        return

    load()
    for i in range(write_report_count):
        write_report()
    set_cursor_to_items()
    for i in range(open_items_count):
        open_items()
    for i in range(watch_steps_count):
        watch_steps()
    