import unittest
from pathlib import Path

import harrixpylib as h


class TestHarrixpylib(unittest.TestCase):
    def test_open_file(self):
        currentdir = Path(__file__).resolve().parent
        s = h.open_file(currentdir / "data\simple_text.txt")
        self.assertEqual(s, "42")

    def test_path_to_pathlib(self):
        currentdir = Path(__file__).resolve().parent
        self.assertEqual(
            h.path_to_pathlib(str(Path(__file__).resolve().parent)), currentdir
        )


if __name__ == "__main__":
    unittest.main()
