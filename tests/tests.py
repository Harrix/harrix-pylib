import unittest
from pathlib import Path

import harrixpylib as h


class TestHarrixpylib(unittest.TestCase):
    def test_open_file(self):
        currentdir = Path(__file__).resolve().parent
        s = h.open_file(currentdir / "data\simple_text.txt")
        self.assertEqual(s, "42")


if __name__ == "__main__":
    unittest.main()
