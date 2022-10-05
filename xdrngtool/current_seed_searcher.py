from xddb import QuickBattleSeedSearcher

from .protocol import OperationReturnsTeamPair, TeamPair

class CurrentSeedSearcher():
    """いますぐバトル生成済み画面から、現在のseedを求める。
    """
    def __init__(self, searcher: QuickBattleSeedSearcher, generate_next_team_pair: OperationReturnsTeamPair) -> None:
        """
        Args:
            searcher (QuickBattleSeedSearcher):
            generate_next_team_pair (OperationReturnsTeamPair): 現在のいますぐバトル生成結果を破棄し、再度生成する
        """
        self.__searcher = searcher
        self.__generate_next_team_pair = generate_next_team_pair

    def search(self):
        self.__searcher.reset()
        while True:
            try:
                generated = self.__generate_next_team_pair.run()
            except:
                raise
            seeds = self.__searcher.next(*generated)
            
            if seeds is None or len(seeds) > 1:
                # None: 足りない
                # len(seeds) > 1: 絞れていない
                continue
            elif len(seeds) == 0:
                # len(seeds) == 0: 見つからなかった
                self.__searcher.reset()
            else:
                return seeds.pop()
