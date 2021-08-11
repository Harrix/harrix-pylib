import unittest
import os
from pathlib import Path

import harrixpylib as h

currentdir = Path(os.path.dirname(os.path.realpath(__file__)))


class TestHarrixpylib(unittest.TestCase):

    def test_open_file(self):
        s = h.open_file(currentdir / 'data/simple_text.txt')
        self.assertEqual(s, '42')

    def test_path_to_pathlib(self):
        self.assertEqual(h.path_to_pathlib(
            os.path.dirname(os.path.realpath(__file__))), currentdir)

    def test_clear_directory(self):
        h.clear_directory(currentdir / 'test_dir')


if __name__ == '__main__':
    unittest.main()
