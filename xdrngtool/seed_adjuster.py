from datetime import timedelta
from typing import Optional, Tuple

from xddb import EnemyTeam, QuickBattleAdvanceEscort, NotFound

from .protocol import ICurrentSeedSearcher, Operation, OperationReturnsTeamPair, OperationTakesTimedelta
from .search_path import search_path
from .util import get_wait_time

class SeedAdjuster():
    """目標のseedまで消費を実行する。
    """
    def __init__(
        self, 
        current_seed_searcher: ICurrentSeedSearcher,
        generate_next_team_pair: OperationReturnsTeamPair,
        enter_wait_and_exit_quick_battle: OperationTakesTimedelta,
        set_cursor_to_setting: Operation,
        change_setting: Operation,
        load: Operation,
        write_report: Operation,

        tsv: Optional[int] = None, 
        advances_by_opening_items: Optional[int] = None,
    ) -> None:
        """
        Args:
            current_seed_searcher (ICurrentSeedSearcher): 
            generate_next_team_pair (OperationReturnsTeamPair): 現在のいますぐバトル生成結果を破棄し、再度生成する
            enter_wait_and_exit_quick_battle (OperationTakesTimedelta): 「このポケモンで　はじめてもよいですか？」「はい」からいますぐバトルを開始し、降参「はい」まで誘導。timedelta時間待機した後、いますぐバトルを降参し、1回いますぐバトルを生成する
            set_cursor_to_setting (Operation): いますぐバトル生成済み画面から、「せってい」にカーソルを合わせる
            change_setting (Operation): 「せってい」にカーソルが合った状態から、設定を変更して保存、「せってい」にカーソルを戻す
            load (Operation): 「せってい」にカーソルが合った状態からロードし、メニューを開き「レポート」にカーソルを合わせる
            write_report (Operation): 「レポート」にカーソルが合った状態から、レポートを書き、「レポート」にカーソルを戻す
            
            tsv (Optional[int]): TSV
            advances_by_opening_items (Optional[int]): もちものを開く際の消費数
        """
        self.__current_seed_searcher = current_seed_searcher
        self.__generate_next_team_pair = generate_next_team_pair
        self.__enter_wait_and_exit_quick_battle = enter_wait_and_exit_quick_battle
        self.__set_cursor_to_setting = set_cursor_to_setting
        self.__change_setting = change_setting
        self.__load = load
        self.__write_report = write_report

        self.__tsv = tsv
        self.__advances_by_opening_items = advances_by_opening_items

    def execute(
        self, 
        target: Tuple[int, timedelta], 
    ) -> None:
        """
        Args:
            target (Tuple[int, timedelta]): 目標seedと待機時間のタプル
        """
        current_seed = _advance_by_moltres(
            self.__current_seed_searcher, self.__generate_next_team_pair, self.__enter_wait_and_exit_quick_battle, 
            target
        )
        escort = QuickBattleAdvanceEscort(current_seed, self.__tsv) if self.__tsv is not None else QuickBattleAdvanceEscort(current_seed)
        _advance_according_to_path(
            escort, self.__current_seed_searcher, self.__generate_next_team_pair, self.__set_cursor_to_setting, self.__change_setting, self.__load, self.__write_report,
            current_seed, target, self.__tsv, self.__advances_by_opening_items
        )
        
def _advance_by_moltres(
    current_seed_searcher: ICurrentSeedSearcher,
    generate_next_team_pair: OperationReturnsTeamPair,
    enter_wait_and_exit_quick_battle: OperationTakesTimedelta,

    target: Tuple[int, timedelta],
) -> int:
    """いますぐバトルにファイヤーを出し、高速消費する。

    Args:
        current_seed_searcher (ICurrentSeedSearcher): 
        generate_next_team_pair (OperationReturnsTeamPair): _description_
        enter_wait_and_exit_quick_battle (OperationTakesTimedelta): _description_
        target (Tuple[int, timedelta]):  目標seedと待機時間のタプル

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

    enter_wait_and_exit_quick_battle.run(target[1])
    
    current_seed = current_seed_searcher.search()
    
    # 待機時間が消費前の待機時間より長いことで、消費しすぎたことを判定
    waited_too_long = get_wait_time(current_seed, target[0]) > target[1]
    if waited_too_long:
        raise Exception("Waited too long.")

    return current_seed

def _advance_according_to_path(
    escort: QuickBattleAdvanceEscort, 
    current_seed_searcher: ICurrentSeedSearcher,
    generate_next_team_pair: OperationReturnsTeamPair,
    set_cursor_to_setting: Operation,
    change_setting: Operation,
    load: Operation,
    write_report: Operation,
    
    current_seed: int,
    target: Tuple[int, timedelta],
    tsv: Optional[int],
    advances_by_opening_items: Optional[int],
):
    """経路を導出し、それに従って消費する。

    Args:
        escort (QuickBattleAdvanceEscort): 
        generate_next_team_pair (OperationReturnsTeamPair): 現在のいますぐバトル生成結果を破棄し、再度生成する
        set_cursor_to_setting (Operation): いますぐバトル生成済み画面から、「せってい」にカーソルを合わせる
        change_setting (Operation): 「せってい」にカーソルが合った状態から、設定を変更して保存、「せってい」にカーソルを戻す
        load (Operation): 「せってい」にカーソルが合った状態からロードし、メニューを開き「レポート」にカーソルを合わせる
        write_report (Operation): 「レポート」にカーソルが合った状態から、レポートを書き、「レポート」にカーソルを戻す

        current_seed (int): 現在のseed
        target (Tuple[int, timedelta]): 目標seedと待機時間のタプル
        tsv (Optional[int]): TSV
        advances_by_opening_items (Optional[int]): もちものを開く際の消費数
    """
    teams, change_setting_count, write_report_count = search_path(current_seed, target[0], tsv, advances_by_opening_items)

    for _ in teams:
        
        team_expected = escort.expected_next()[:2]
        team_generated = generate_next_team_pair.run()

        ret = escort.next(*team_generated)
        if isinstance(ret, NotFound):
            conflict = current_seed_searcher.search()
            _advance_according_to_path(
                QuickBattleAdvanceEscort(conflict, tsv) if tsv is not None else QuickBattleAdvanceEscort(conflict), current_seed_searcher, generate_next_team_pair, set_cursor_to_setting, change_setting, load, write_report,
                conflict, target, tsv, advances_by_opening_items
            )
            return

        if team_expected != team_generated:
            _advance_according_to_path(
                escort, current_seed_searcher, generate_next_team_pair, set_cursor_to_setting, change_setting, load, write_report,
                ret.current_seed, target, tsv, advances_by_opening_items
            )
            return
    
    set_cursor_to_setting.run()
    for _ in range(change_setting_count):
        change_setting.run()
    
    if advances_by_opening_items is None:
        return

    load.run()
    for _ in range(write_report_count):
        write_report.run()
