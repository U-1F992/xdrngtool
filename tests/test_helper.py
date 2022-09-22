from datetime import timedelta
from typing import Generator
import unittest
from xdhelper import *

class TestHelper(unittest.TestCase):
    
    def test_get_wait_time(self):
        test_case = [
            (0x0, 0xca71efd8, timedelta(hours=1)),
        ]
        for current_seed, target_seed, expected in test_case:
            with self.subTest(current_seed=current_seed, target_seed=target_seed, expected=expected):
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
            with self.subTest(current_seed=current_seed, target_seed=target_seed, expected=expected):
                actual = get_route(current_seed, target_seed)
                self.assertEqual(expected[0], len(actual[0]))
                self.assertEqual(expected[1], actual[1])
    
    def test_get_route_2(self):
        """ロードする場合
        """
        DEFAULT_TSV = 65536
        test_case = [
            (0xfe645768, 0xff7eafab, DEFAULT_TSV, (24, 13), (688, 0, 7, 0, 0)),
            (0x88144b1c, 0x143956ec, DEFAULT_TSV, (24, 13), (0, 1, 0, 0, 8)),
        ]
        for current_seed, target_seed, tsv, opts, expected in test_case:
            with self.subTest(current_seed=current_seed, target_seed=target_seed, tsv=tsv, opts=opts, expected=expected):
                actual = get_route(current_seed, target_seed, tsv, opts)
                self.assertEqual(expected[0], len(actual[0]))
                self.assertEqual(expected[1], actual[1])
                self.assertEqual(expected[2], actual[2])
                self.assertEqual(expected[3], actual[3])
                self.assertEqual(expected[4], actual[4])
    
    def test_get_current_seed(self):
        DEFAULT_TSV = 65536
        test_case = [
            # ([], DEFAULT_TSV, 0x0),
            # 2回で見つかるもの
            # 3回で見つかるもの
            # 4回（以上）で見つかるもの
            # 途中で見失うもの
        ]
        for sequence, tsv, expected in test_case:
            with self.subTest(sequence=sequence, tsv=tsv, expected=expected):
                actual = get_current_seed(mock_generator(sequence), tsv)
                self.assertEqual(expected, actual)

def mock_generator(sequence: list[int]) -> Generator[int, None, None]:
    for item in sequence:
        yield item
    return

if __name__ == "__main__":
    unittest.main()
