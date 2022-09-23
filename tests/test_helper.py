from datetime import timedelta
from typing import Generator, TypeVar
import unittest
from xdrngtool import *

class TestHelper(unittest.TestCase):
    
    def test_get_wait_time(self):
        test_case = [
            (0x0, 0xca71efd8, timedelta(hours=1)),
        ]
        for current_seed, target_seed, expected in test_case:
            with self.subTest(current_seed=f"{current_seed:X}", target_seed=f"{target_seed:X}", expected=expected):
                actual = get_wait_time(current_seed, target_seed)
                self.assertEqual(expected, actual)

    def test_is_suitable_for_waiting(self):
        test_case = [
            (timedelta(seconds=1), False),
            (timedelta(minutes=5), True),
            (timedelta(hours=12), False),
        ]
        for wait_time, expected in test_case:
            with self.subTest(wait_time=wait_time, expected=expected):
                actual = is_suitable_for_waiting(wait_time)
                self.assertEqual(expected, actual)

    def test_get_route_1(self):
        """ロードしない場合
        """
        test_case = [
            (0x88144b1c, 0xd3dfba89, (1, 0)),
            (0x88144b1c, 0x143956ec, (0, 2)),
            (0x814fe9dd, 0xb11b9415, (10, 10)),
            (0x410df1e7, 0xbfb6e0c8, (5, 0)),
        ]
        for current_seed, target_seed, expected in test_case:
            with self.subTest(current_seed=f"{current_seed:X}", target_seed=f"{target_seed:X}", expected=expected):
                actual = get_route(current_seed, target_seed)
                self.assertEqual(expected[0], len(actual[0]))
                self.assertEqual(expected[1], actual[1])
    
    def test_get_route_2(self):
        """ロードする場合
        """
        test_case = [
            (0xfe645768, 0xff7eafab, DEFAULT_TSV, (24, 13), (688, 0, 7, 0, 0)),
            (0x88144b1c, 0x143956ec, DEFAULT_TSV, (24, 13), (0, 1, 0, 0, 8)),
        ]
        for current_seed, target_seed, tsv, opts, expected in test_case:
            with self.subTest(current_seed=f"{current_seed:X}", target_seed=f"{target_seed:X}", tsv=tsv, opts=opts, expected=expected):
                actual = get_route(current_seed, target_seed, tsv, opts)
                self.assertEqual(expected[0], len(actual[0]))
                self.assertEqual(expected[1], actual[1])
                self.assertEqual(expected[2], actual[2])
                self.assertEqual(expected[3], actual[3])
                self.assertEqual(expected[4], actual[4])
    
    def test_get_current_seed(self):
        test_case: list[tuple[list[TeamPair, int, int]]] = [
            # 2回で見つかるもの
            (
                [
                    ((PlayerTeam.Rayquaza, 346, 235), (EnemyTeam.Zapdos, 313, 317)),
                    ((PlayerTeam.Mewtwo, 395, 346), (EnemyTeam.Kangaskhan, 350, 335))
                ],
                DEFAULT_TSV, 0x4d8483e7
            ),
            (
                [
                    ((PlayerTeam.Mew, 328, 344), (EnemyTeam.Latias, 344, 279)),
                    ((PlayerTeam.Mew, 336, 304), (EnemyTeam.Zapdos, 321, 311))
                ],
                DEFAULT_TSV, 0x6E4EF1C9
            ),
            # 3回で見つかるもの
            # (
            #     [
            #         ((PlayerTeam.Mewtwo, 362, 349), (EnemyTeam.Articuno, 320, 388)),
            #         ((PlayerTeam.Mewtwo, 342, 352), (EnemyTeam.Articuno, 325, 384)),
            #         ((PlayerTeam.Mewtwo, 335, 382), (EnemyTeam.Articuno, 331, 361)),
            #     ],
            #     1784, 0xd9202593
            # ),
            # 4回（以上）で見つかるもの
            # 途中で見失うもの
        ]
        for sequence, tsv, expected in test_case:
            with self.subTest(sequence=sequence, tsv=tsv, expected=f"{expected:X}"):
                generator = (item for item in sequence)
                actual = get_current_seed(generator, tsv)
                self.assertEqual(expected, actual)

if __name__ == "__main__":
    unittest.main()
