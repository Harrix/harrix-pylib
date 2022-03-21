import unittest
import os
from pathlib import Path

import harrixpylib as h


class TestHarrixpylib(unittest.TestCase):
    def test_clear_directory__01(self):
        folder = Path(__file__).resolve().parent / "data/temp"
        folder.mkdir(parents=True, exist_ok=True)
        Path(folder / "temp.txt").write_text("Hello, world!", encoding="utf8")
        h.clear_directory(folder)
        self.assertEqual(len(next(os.walk(folder))[2]), 0)

    def test_remove_yaml_from_markdown__01(self):
        current_folder = Path(__file__).resolve().parent
        filename = current_folder / "data/article.md"
        md = Path(filename).read_text(encoding="utf8")
        md_clean = h.remove_yaml_from_markdown(md)
        self.assertEqual(len(md_clean.splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
