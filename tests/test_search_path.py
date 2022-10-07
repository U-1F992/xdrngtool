from typing import List, Optional, Set, Tuple
import unittest

from lcg.gc import LCG
from xddb import generate_quick_battle
from xdrngtool import search_path, TeamPair

def _advance_according_to_path(current_seed: int, path: Tuple[List[Tuple[TeamPair, int, Set[int]]], int, int], tsv: Optional[int], advances_by_opening_items: Optional[int]) -> int:
    lcg = LCG(current_seed)
    teams, change_setting, write_report = path
    # （teamsの個数）回生成
    for _ in teams:
        generate_quick_battle(lcg, tsv)
    # 設定変更
    lcg.adv(40 * change_setting)
    if advances_by_opening_items is None:
        return lcg.seed
    # ロードしてレポート
    lcg.adv((advances_by_opening_items - 1) * 2)
    lcg.adv(63 * write_report)
    return lcg.seed

class TestSearchPath(unittest.TestCase):
    def test_search_path(self):
        test_case = [
            (0x88144b1c, 0xd3dfba89, None, None),
            (0x814fe9dd, 0xb11b9415, None, None),
            (0x410df1e7, 0xbfb6e0c8, None, None),
            (0xfe645768, 0xff7eafab, None, 13),
            (0x941a74bb, 0x4f9370a0, None, 17)
        ]
        for current_seed, expected, tsv, advances_by_opening_items in test_case:
            
            with self.subTest(current_seed=f"{current_seed:X}", expected=f"{expected:X}", tsv=tsv, advances_by_opening_items=advances_by_opening_items):
                path = search_path(current_seed, expected, tsv, advances_by_opening_items)
                actual = _advance_according_to_path(current_seed, path, tsv, advances_by_opening_items)
                self.assertEqual(expected, actual)

if __name__ == "__main__":
    unittest.main()
