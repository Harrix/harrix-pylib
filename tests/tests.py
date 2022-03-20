import unittest
import os
from pathlib import Path

import harrixpylib as h


class TestHarrixpylib(unittest.TestCase):
    def test_open_file(self):
        current_folder = Path(__file__).resolve().parent
        s = h.open_file(current_folder / "data/simple_text.txt")
        self.assertEqual(s, "42")

    def test_clear_directory(self):
        folder = Path(__file__).resolve().parent / "data/test"
        folder.mkdir(parents=True, exist_ok=True)
        h.save_file("Hello, world!", folder / "text.txt")
        h.clear_directory(folder)
        self.assertEqual(len(next(os.walk(folder))[2]), 0)


if __name__ == "__main__":
    unittest.main()
