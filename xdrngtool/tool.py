from time import sleep
from typing import Callable, Generator
from .helper import *

class XDRNGTool():
    
    def __init__(
        self,
        transition_to_quick_battle: Callable[[], None],
        generate_next_team_pair: Callable[[], TeamPair],
        enter_quick_battle: Callable[[], None],
        exit_quick_battle: Callable[[], None],

        # 消費関連の動作

        verifier: Callable[[], bool],
    ) -> None:
        self.transition_to_quick_battle = transition_to_quick_battle
        self.generate_next_team_pair = generate_next_team_pair
        self.enter_quick_battle = enter_quick_battle
        self.exit_quick_battle = exit_quick_battle
        self.verifier = verifier
    
    def execute(self, target_seeds: list[int], tsv: int, opts: tuple[int, int] | None) -> bool:

        # 初期seed厳選
        current_seed, target = self.decide_target(tsv)
        
        try:
            # いますぐバトルで大量消費し、再度現在のseedを確認
            current_seed = self.advance_by_moltres(target[1])
            
            # 経路に従い消費
            self.follow_route(current_seed, target, tsv, opts)
        except:
            return self.execute(target_seeds, tsv, opts)
        
        # seed調整後に行う動作を実行
        return self.verifier()

    def decide_target(self, target_seeds: list[int], tsv: int) -> tuple[int, tuple[int, timedelta]]:

        # 初期seed厳選

        current_seed: int = int()
        target: tuple[int, timedelta] = (int(), timedelta())

        while True:
            self.transition_to_quick_battle()
            try:
                current_seed = get_current_seed(self.generate_next_team_pair, tsv)
            except:
                continue
            
            target = sorted(
                [(target_seed, get_wait_time(current_seed, target_seed)) for target_seed in target_seeds]
            )[0]
            
            if is_suitable_for_waiting(target[1]):
                break
        return current_seed, target

    def advance_by_moltres(self, target: tuple[int, timedelta], tsv: int) -> int:

        # いますぐバトル生成済み画面から
        # 1. ファイヤーが出るまで再生成
        # 2. 戦闘に入りwait_time待機
        # 3. 戦闘から出て再度現在のseedを特定

        while True:
            team_pair = self.generate_next_team_pair()
            if team_pair[1][0] == EnemyTeam.Moltres:
                break

        self.enter_quick_battle()
        sleep(target[1].total_seconds)
        self.exit_quick_battle()
        
        current_seed = get_current_seed(self.generate_next_team_pair, tsv)
        
        # 待機時間が消費前の待機時間より長いことで、消費しすぎたことを判定
        waited_too_long = get_wait_time(current_seed, target[0]) > target[1]
        if waited_too_long:
            raise Exception("Waited too long.")

        return current_seed

    def follow_route(self, current_seed: int, target: tuple[int, timedelta], tsv: int, opts: tuple[int, int] | None) -> None:

        # 経路に従って消費する

        route = get_route(current_seed, target[0], tsv, opts)

        pass