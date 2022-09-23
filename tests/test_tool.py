from typing import Generator
from xdrngtool import *

def transition_to_quick_battle() -> None:

    # リセットし、いますぐバトル生成済み画面まで遷移する（1回目は捨てる）
    
    pass

def generate_next_team_pair() -> TeamPair:
    
    # いますぐバトル生成済み画面から
    # 1. B入力（破棄）
    # 2. A入力（生成）
    # 3. 画像認識
    # して、TeamPairをyieldするジェネレータ

    # 操作の暴発などで回復不能になった場合はreturnかraiseで脱出する
    
    pass

def enter_quick_battle() -> None:
    pass
def exit_quick_battle() -> None:
    pass

def verify_if_operation_succeeded() -> bool:

    # seed調整後に行う動作を書き、成否を返す
    # エンカウント・捕獲・HP素早さ判定・ID生成など...

    return True

if __name__ == "__main__":
    
    target_seeds: list[int] = [0xdeadface]
    tsv: int = DEFAULT_TSV
    opts: tuple[int, int] | None = None

    tool = XDRNGTool(
        transition_to_quick_battle,
        generate_next_team_pair,
        enter_quick_battle,
        exit_quick_battle,
        verify_if_operation_succeeded
    )

    while not XDRNGTool().execute(target_seeds, tsv, opts):
        pass
