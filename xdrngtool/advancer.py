from datetime import timedelta
from time import sleep
from typing import Optional, Tuple

from lcg.gc import LCG
from xddb import EnemyTeam, generate_quick_battle

from .current_seed_searcher import CurrentSeedSearcher
from .protocol import Operation, TeamPair
from .util import decide_route, decode_quick_battle, get_wait_time

class Advancer():
    """目標のseedまで消費を実行する。
    """
    def __init__(
        self, 
        current_seed_searcher: CurrentSeedSearcher,
        generate_next_team_pair: Operation[TeamPair],
        enter_quick_battle: Operation[None],
        exit_quick_battle: Operation[None],
        set_cursor_to_setting: Operation[None],
        change_setting: Operation[None],
        load: Operation[None],
        write_report: Operation[None],
        set_cursor_to_items: Operation[None],
        open_items: Operation[None],
        watch_steps: Operation[None],
    ) -> None:
        """
        Args:
            current_seed_searcher (CurrentSeedSearcher): 
            generate_next_team_pair (Operation[TeamPair]): 現在のいますぐバトル生成結果を破棄し、再度生成する
            enter_quick_battle (Operation[None]): 「このポケモンで　はじめてもよいですか？」「はい」からいますぐバトルを開始し、降参「はい」まで誘導する
            exit_quick_battle (Operation[None]): 降参「はい」からいますぐバトルを降参し、1回いますぐバトルを生成する
            set_cursor_to_setting (Operation[None]): いますぐバトル生成済み画面から、「せってい」にカーソルを合わせる
            change_setting (Operation[None]): 「せってい」にカーソルが合った状態から、設定を変更して保存、「せってい」にカーソルを戻す
            load (Operation[None]): 「せってい」にカーソルが合った状態からロードし、メニューを開き「レポート」にカーソルを合わせる
            write_report (Operation[None]): 「レポート」にカーソルが合った状態から、レポートを書き、「レポート」にカーソルを戻す
            set_cursor_to_items (Operation[None]): 「レポート」にカーソルが合った状態から、「もちもの」にカーソルを合わせる
            open_items (Operation[None]): 「もちもの」にカーソルが合った状態から、もちものを開いて閉じる
            watch_steps (Operation[None]): メニューが開いている状態から、メニューを閉じ1回腰振りさせ、再度メニューを開く
        """
        self.__current_seed_searcher = current_seed_searcher
        self.__generate_next_team_pair = generate_next_team_pair
        self.__enter_quick_battle = enter_quick_battle
        self.__exit_quick_battle = exit_quick_battle
        self.__set_cursor_to_setting = set_cursor_to_setting
        self.__change_setting = change_setting
        self.__load = load
        self.__write_report = write_report
        self.__set_cursor_to_items = set_cursor_to_items
        self.__open_items = open_items
        self.__watch_steps = watch_steps

    def execute(
        self, 
        target: Tuple[int, timedelta], 
        tsv: Optional[int], 
        advances_by_opening_items: Optional[int],
    ) -> None:
        """
        Args:
            target (Tuple[int, timedelta]): 目標seedと待機時間のタプル
            tsv (Optional[int]): TSV
            advances_by_opening_items (Optional[int]): もちものを開く際の消費数
        """
        current_seed = __advance_by_moltres(self.__generate_next_team_pair, self.__enter_quick_battle, self.__exit_quick_battle, target, tsv)
        __advance_according_to_route(self.__current_seed_searcher, self.__generate_next_team_pair, self.__set_cursor_to_setting, self.__change_setting, self.__load, self.__write_report, self.__set_cursor_to_items, self.__open_items, self.__watch_steps, current_seed, target, tsv, advances_by_opening_items)
        
def __advance_by_moltres(
    current_seed_searcher: CurrentSeedSearcher,
    generate_next_team_pair: Operation[TeamPair],
    enter_quick_battle: Operation[None],
    exit_quick_battle: Operation[None],

    target: Tuple[int, timedelta],
    tsv: Optional[int],
) -> int:
    """いますぐバトルにファイヤーを出し、高速消費する。

    Args:
        current_seed_searcher (CurrentSeedSearcher): 
        generate_next_team_pair (Operation[TeamPair]): _description_
        enter_quick_battle (Operation[None]): _description_
        exit_quick_battle (Operation[None]): _description_
        target (Tuple[int, timedelta]):  目標seedと待機時間のタプル
        tsv (Optional[int]): TSV

    Raises:
        Exception: _description_

    Returns:
        int: 高速消費後の現在のseed
    """
    
    # いますぐバトル生成済み画面から
    # 1. ファイヤーが出るまで再生成
    # 2. 戦闘に入りwait_time待機
    # 3. 戦闘から出て再度現在のseedを特定

    while True:
        team_pair = generate_next_team_pair.run()
        if team_pair[1][0] == EnemyTeam.Moltres:
            break

    enter_quick_battle.run()
    sleep(target[1].total_seconds())
    exit_quick_battle.run()
    
    current_seed = current_seed_searcher.search()
    
    # 待機時間が消費前の待機時間より長いことで、消費しすぎたことを判定
    waited_too_long = get_wait_time(current_seed, target[0]) > target[1]
    if waited_too_long:
        raise Exception("Waited too long.")

    return current_seed

def __advance_according_to_route(
    current_seed_searcher: CurrentSeedSearcher,
    generate_next_team_pair: Operation[TeamPair],
    set_cursor_to_setting: Operation[None],
    change_setting: Operation[None],
    load: Operation[None],
    write_report: Operation[None],
    set_cursor_to_items: Operation[None],
    open_items: Operation[None],
    watch_steps: Operation[None],
    
    current_seed: int,
    target: Tuple[int, timedelta],
    tsv: Optional[int],
    advances_by_opening_items: Optional[int],
):
    """経路を導出し、それに従って消費する。

    Args:
        current_seed_searcher (CurrentSeedSearcher): 
        generate_next_team_pair (Operation[TeamPair]): 現在のいますぐバトル生成結果を破棄し、再度生成する
        set_cursor_to_setting (Operation[None]): いますぐバトル生成済み画面から、「せってい」にカーソルを合わせる
        change_setting (Operation[None]): 「せってい」にカーソルが合った状態から、設定を変更して保存、「せってい」にカーソルを戻す
        load (Operation[None]): 「せってい」にカーソルが合った状態からロードし、メニューを開き「レポート」にカーソルを合わせる
        write_report (Operation[None]): 「レポート」にカーソルが合った状態から、レポートを書き、「レポート」にカーソルを戻す
        set_cursor_to_items (Operation[None]): 「レポート」にカーソルが合った状態から、「もちもの」にカーソルを合わせる
        open_items (Operation[None]): 「もちもの」にカーソルが合った状態から、もちものを開いて閉じる
        watch_steps (Operation[None]): メニューが開いている状態から、メニューを閉じ1回腰振りさせ、再度メニューを開く

        current_seed (int): 現在のseed
        target (Tuple[int, timedelta]): 目標seedと待機時間のタプル
        tsv (Optional[int]): TSV
        advances_by_opening_items (Optional[int]): もちものを開く際の消費数
    """
    teams, change_setting_count, write_report_count, open_items_count, watch_steps_count = decide_route(current_seed, target[0], tsv, advances_by_opening_items)

    for team_seed_psvs in teams:
        
        team_expected, seed_before, psvs = team_seed_psvs
        team_generated = generate_next_team_pair.run()

        # 生成結果と予測が異なる場合、色回避によって生成ルートが変更される（TSVを指定しなかった、指定したTSVが誤っていたなど）
        # - psvをtsvに設定して一致するものがあれば、そこから復帰
        # - psvのいずれをtsvに設定しても一致するものがなければ、現在seedを再特定して復帰
        
        if team_generated != team_expected:

            for tsv_suggested in psvs:
                _lcg = LCG(seed_before)
                team_suggested, _ = decode_quick_battle(generate_quick_battle(_lcg, tsv_suggested))
                if team_generated == team_suggested:
                    __advance_according_to_route(_lcg.seed, target, tsv, advances_by_opening_items)
                    return

            conflict_current_seed = current_seed_searcher.search()
            __advance_according_to_route(conflict_current_seed, target, tsv, advances_by_opening_items)
            return
    
    set_cursor_to_setting.run()
    for _ in range(change_setting_count):
        change_setting.run()
    
    if advances_by_opening_items is None:
        return

    load.run()
    for _ in range(write_report_count):
        write_report.run()
    set_cursor_to_items.run()
    for _ in range(open_items_count):
        open_items.run()
    for _ in range(watch_steps_count):
        watch_steps.run()
