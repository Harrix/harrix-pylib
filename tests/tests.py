import unittest
import os, sys
from pathlib import Path

import harrixpylib as h


class TestHarrixpylib(unittest.TestCase):
    def test_open_file(self):
        currentdir = Path(os.path.dirname(os.path.realpath(__file__)))
        s = h.open_file(currentdir / "data/simple_text.txt")
        self.assertEqual(s, "42")

    def test_path_to_pathlib(self):
        currentdir = Path(os.path.dirname(os.path.realpath(__file__)))
        self.assertEqual(
            h.path_to_pathlib(os.path.dirname(os.path.realpath(__file__))), currentdir
        )


if __name__ == "__main__":
    unittest.main()
