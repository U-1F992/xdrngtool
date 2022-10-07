from datetime import timedelta
from typing import List
import unittest

from xdrngtool import TargetSelector
from mocks import MockCurrentSeedSearcher, MockOperation

def _format_seeds(seeds: List[int]):
    return [f"{seed:X}" for seed in seeds]

class TestTargetSelector(unittest.TestCase):
    def test_target_selector(self):
        test_case = [
            (
                [0xbeef],
                [0x2a9a6eef],
                timedelta(seconds=3538, microseconds=125976)
            )
        ]
        for current_seeds, target_seeds, expected in test_case:

            current_seed_searcher = MockCurrentSeedSearcher(current_seeds)
            operation = MockOperation()
            target_selector = TargetSelector(current_seed_searcher, operation)

            with self.subTest(current_seeds=_format_seeds(current_seeds), target_seed=_format_seeds(target_seeds), expected=expected):
                actual = target_selector.execute(target_seeds)
                self.assertEqual(expected, actual[1][1])

if __name__ == "__main__":
    unittest.main()
