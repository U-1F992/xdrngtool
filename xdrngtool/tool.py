from typing import Callable, TypeAlias

from .constant import DEFAULT_TSV
from .helper import *

Operations: TypeAlias = tuple[
    Callable[[], None],
    Callable[[], TeamPair],
    Callable[[], None],
    Callable[[], None],
    Callable[[], None],
    Callable[[], None],
    Callable[[], None],
    Callable[[], None],
    Callable[[], None],
    Callable[[], None],
    Callable[[], None]
]

def execute_operation(
    operations: Operations, 
    verifier: Callable[[], bool],
    target_seeds: list[int], 
    tsv: int = DEFAULT_TSV, 
    opts: tuple[int, int] | None = None, 
) -> bool:
    """ポケモンXDの乱数調整を行います。

    タプルには以下を動作を行うコールバック関数を登録します

    - リセットし、1回いますぐバトルを生成した画面まで誘導する\n
    - 現在のいますぐバトル生成結果を破棄し、再度生成して渡す\n
    - いますぐバトル生成済み画面から、「せってい」にカーソルを合わせる\n
    - 「せってい」にカーソルが合った状態から、設定を変更して保存、「せってい」にカーソルを戻す\n
    - 「せってい」にカーソルが合った状態からロードし、メニューを開き「レポート」にカーソルを合わせる\n
    - 「レポート」にカーソルが合った状態から、レポートを書き、「レポート」にカーソルを戻す\n
    - 「レポート」にカーソルが合った状態から、「もちもの」にカーソルを合わせる\n
    - 「もちもの」にカーソルが合った状態から、もちものを開いて閉じる\n
    - メニューが開いている状態から、メニューを閉じ腰振り1回分待機し、メニューを開く\n

    Args:
        operations (Operations): 上記参照
        verifier (Callable[[], bool]): seed調整後に実行し、成否を返すコールバック関数（エンカウント・捕獲・HP素早さ判定・ID生成など...）
        target_seeds (list[int]): 目標seedのリスト
        tsv (int): TSV。指定しない場合、いますぐバトルの生成結果に齟齬が生じ再計算が発生する可能性があります。 Defaults to DEFAULT_TSV.
        opts (tuple[int, int] | None): ロード後に使用する消費数（ロード時の強制消費数、もちものを開く際の消費数）。 Defaults to None.

    Returns:
        bool: 試行の成否
    """
    
    (
        transition_to_quick_battle, 
        generate_next_team_pair, 
        enter_quick_battle, 
        exit_quick_battle, 
        set_cursor_to_setting, 
        change_setting, 
        load, 
        write_report, 
        set_cursor_to_items, 
        open_items, 
        watch_steps
    ) = operations

    current_seed, target = decide_target(target_seeds, tsv, transition_to_quick_battle, generate_next_team_pair)
    
    try:
        current_seed = advance_by_moltres(target[1], tsv, generate_next_team_pair, enter_quick_battle, exit_quick_battle)
        advance_according_to_route(current_seed, target, tsv, opts, generate_next_team_pair, set_cursor_to_setting, change_setting, load, write_report, set_cursor_to_items, open_items, watch_steps)
    except:
        return execute_operation(target_seeds, tsv, opts)
    
    return verifier()
