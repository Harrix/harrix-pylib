import os
from pathlib import Path
import shutil
import webbrowser

import harrixpylib as h


if __name__ == "__main__":
    root_folder = Path(__file__).resolve().parent.parent
    h.clear_directory(root_folder / "docs")
    os.system('pdoc -o ./docs --docformat="google" src\\harrixpylib\\')
    path_img = root_folder / "src_docs/img"
    if path_img.is_dir():
        shutil.copytree(
            path_img,
            root_folder / "docs/harrixpylib/img",
            dirs_exist_ok=True,
        )
    url = f"file:///{str(root_folder)}/docs/index.html"
    webbrowser.open(url, new=2)
