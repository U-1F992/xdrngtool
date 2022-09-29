from abc import ABC, abstractmethod
from typing import Tuple

from xddb import EnemyTeam, PlayerTeam

# いますぐバトルの生成結果を表すTypeAlias
TeamPair = Tuple[Tuple[PlayerTeam, int, int], Tuple[EnemyTeam, int, int]]

class XDRNGOperations(ABC):
    """ポケモンXD乱数調整において使用する各操作を定義する抽象クラス
    """
    @abstractmethod
    def transition_to_quick_battle(self) -> None:
        """リセットし、1回いますぐバトル（さいきょう）を生成した画面まで誘導する
        """
        pass
    @abstractmethod
    def generate_next_team_pair(self) -> TeamPair:
        """現在のいますぐバトル生成結果を破棄し、再度生成する

        Returns:
            TeamPair: いますぐバトル生成結果
        """
        pass 
    @abstractmethod
    def enter_quick_battle(self) -> None:
        """「このポケモンで　はじめてもよいですか？」「はい」からいますぐバトルを開始し、降参「はい」まで誘導する
        """
        pass 
    @abstractmethod
    def exit_quick_battle(self) -> None:
        """降参「はい」からいますぐバトルを降参し、1回いますぐバトルを生成する
        """
        pass 
    @abstractmethod
    def set_cursor_to_setting(self) -> None:
        """いますぐバトル生成済み画面から、「せってい」にカーソルを合わせる
        """
        pass 
    @abstractmethod
    def change_setting(self) -> None:
        """「せってい」にカーソルが合った状態から、設定を変更して保存、「せってい」にカーソルを戻す
        """
        pass 
    @abstractmethod
    def load(self) -> None:
        """「せってい」にカーソルが合った状態からロードし、メニューを開き「レポート」にカーソルを合わせる
        """
        pass 
    @abstractmethod
    def write_report(self) -> None:
        """「レポート」にカーソルが合った状態から、レポートを書き、「レポート」にカーソルを戻す
        """
        pass 
    @abstractmethod
    def set_cursor_to_items(self) -> None:
        """「レポート」にカーソルが合った状態から、「もちもの」にカーソルを合わせる
        """
        pass 
    @abstractmethod
    def open_items(self) -> None:
        """「もちもの」にカーソルが合った状態から、もちものを開いて閉じる
        """
        pass 
    @abstractmethod
    def watch_steps(self) -> None:
        """メニューが開いている状態から、メニューを閉じ1回腰振りさせ、再度メニューを開く
        """
        pass
    @abstractmethod
    def verify(self) -> bool:
        """乱数調整の成否を検証する。

        ロードしない場合は「レポート」にカーソルが合った状態、ロードする場合はメニューを開き「もちもの」にカーソルが合った状態から開始する。

        エンカウント・捕獲・HP素早さ判定・ID生成など...

        Returns:
            bool: 乱数調整の成否
        """
        pass
    