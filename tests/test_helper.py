import unittest
from xdhelper.helper import *

class TestHelper(unittest.TestCase):
    
    def test_get_wait_time(self):
        test_case = [
            (0x0, 0xFFFFFFFF, timedelta())
        ]
        for _ in test_case:
            current_seed, target_seed, expected = _
            actual = get_wait_time(current_seed, target_seed)
            self.assertEqual(expected, actual)

    def is_short_enough(self):
        test_case = [
            (timedelta(seconds=1), False),
            (timedelta(minutes=5), True),
            (timedelta(hours=12), False),
        ]
        for _ in test_case:
            wait_time, expected = _
            actual = is_short_enough(wait_time)
            self.assertEqual(expected, actual)

    def get_route(self):
        pass

if __name__ == "__main__":
    unittest.main()
