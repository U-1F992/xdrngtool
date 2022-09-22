import unittest
from xdhelper.helper import *

class TestHelper(unittest.TestCase):
    
    def test_get_wait_time(self):
        test_case = [
            (0x0, 0xCA71EFD8, timedelta(hours=1)),
        ]
        for current_seed, target_seed, expected in test_case:
            with self.subTest(current_seed=current_seed, target_seed=target_seed, expected=expected):
                actual = get_wait_time(current_seed, target_seed)
                self.assertEqual(expected, actual)

    def test_is_short_enough(self):
        test_case = [
            (timedelta(seconds=1), False),
            (timedelta(minutes=5), True),
            (timedelta(hours=12), False),
        ]
        for wait_time, expected in test_case:
            with self.subTest(wait_time=wait_time, expected=expected):
                actual = is_short_enough(wait_time)
                self.assertEqual(expected, actual)

    def get_route(self):
        pass

if __name__ == "__main__":
    unittest.main()
