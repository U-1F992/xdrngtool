from datetime import timedelta
from typing import Callable, Generator
from xdhelper import *

def transition_to_quick_battle() -> None:

    # リセットし、いますぐバトル生成済み画面まで遷移する（1回目は捨てる）
    
    pass

def generate_next_team_pair() -> Generator[TeamPair, None, None]:
    
    # いますぐバトル生成済み画面から
    # 1. B入力（破棄）
    # 2. A入力（生成）
    # 3. 画像認識
    # して、TeamPairをyieldするジェネレータ

    # 操作の暴発などで回復不能になった場合はreturnかraiseで脱出する
    
    pass

def decide_target(target_seeds: list[int], tsv: int) -> tuple[int, tuple[int, timedelta]]:

    # 初期seed厳選

    current_seed: int = int()
    target: tuple[int, timedelta] = (int(), timedelta())

    while True:
        transition_to_quick_battle()
        try:
            current_seed = get_current_seed(generate_next_team_pair(), tsv)
        except:
            continue
        
        target = sorted(
            [(target_seed, get_wait_time(current_seed, target_seed)) for target_seed in target_seeds]
        )[0]
        
        if is_suitable_for_waiting(target[1]):
            break
    return current_seed, target

def advance_by_moltres(target: tuple[int, timedelta], tsv: int) -> int:

    # いますぐバトル生成済み画面から
    # 1. ファイヤーが出るまで再生成
    # 2. 戦闘に入りwait_time待機
    # 3. 戦闘から出て再度現在のseedを特定
    
    current_seed = get_current_seed(generate_next_team_pair(), tsv)
    
    # 待機時間が消費前の待機時間より長いことで、消費しすぎたことを判定
    waited_too_long = get_wait_time(current_seed, target[0]) > target[1]
    if waited_too_long:
        raise Exception("Waited too long.")

    return current_seed

def follow_route(route: tuple[list[TeamPair], int, int, int, int]) -> None:

    # 経路に従って消費する

    pass

def execute_xd_rng(target_seeds: list[int], tsv: int, opts: tuple[int, int] | None, verifier: Callable[[], bool]) -> bool:

    # 初期seed厳選
    current_seed, target = decide_target(tsv)
    
    # いますぐバトルで大量消費し、再度現在のseedを確認
    try:
        current_seed = advance_by_moltres(target[1])
    except:
        return execute_xd_rng(target_seeds, tsv, opts, verifier)
    
    # 経路に従い消費
    try:
        route = get_route(current_seed, target[0], tsv, opts)
        follow_route(route)
    except:
        return execute_xd_rng(target_seeds, tsv, opts, verifier)

    # seed調整後に行う動作を実行
    return verifier()

def verify_if_operation_succeeded() -> bool:

    # seed調整後に行う動作を書き、成否を返す
    # エンカウント・捕獲・HP素早さ判定・ID生成など...

    return True

if __name__ == "__main__":
    
    target_seeds: list[int] = [0xdeadface]
    tsv: int = DEFAULT_TSV
    opts: tuple[int, int] | None = None

    while not execute_xd_rng(target_seeds, tsv, opts, verify_if_operation_succeeded):
        pass
