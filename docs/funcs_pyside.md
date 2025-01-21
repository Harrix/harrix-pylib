---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# File `funcs_pyside.py`

## Function `create_emoji_icon`

```python
def create_emoji_icon(emoji: str, size: int = 32) -> QIcon
```

Creates an icon with the given emoji.

Args:

- `emoji` (`str`): The emoji to be used in the icon.
- `size` (`int`): The size of the icon in pixels. Defaults to `32`.

Returns:

- `QIcon`: A QIcon object containing the emoji as an icon.

Examples:

```python
import harrix_pylib as h

icon = h.pyside.create_emoji_icon("❌")
```

```python
import harrix_pylib as h
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QAction

app = QApplication([])

action = QAction(h.pyside.create_emoji_icon("❌"),"Test", triggered=lambda: print("Test"))
```

<details>
<summary>Code:</summary>

```python
def create_emoji_icon(emoji: str, size: int = 32) -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    font = QFont()
    font.setPointSize(int(size * 0.8))
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignCenter, emoji)
    painter.end()

    return QIcon(pixmap)
```

</details>

## Function `generate_markdown_from_qmenu`

```python
def generate_markdown_from_qmenu(menu: QMenu, level: int = 0) -> List[str]
```

Generates a markdown representation of a QMenu structure.

This function traverses the QMenu and its submenus to produce a nested list in markdown format.

Args:

- `menu` (`QMenu`): The QMenu object to convert to markdown.
- `level` (`int`, optional): The current indentation level for nested menus. Defaults to `0`.

Returns:

- `List[str]`: A list of strings, each representing a line of markdown text that describes the menu structure.

Example:

```python
import harrix_pylib as h
from PySide6.QtWidgets import QApplication, QMenu
from PySide6.QtGui import QAction

app = QApplication([])

main_menu = QMenu("Main Menu")
submenu1 = QMenu("Submenu 1")
submenu2 = QMenu("Submenu 2")
main_menu.addAction(QAction("Item 1", main_menu))
main_menu.addMenu(submenu1)
main_menu.addAction(QAction("Item 2", main_menu))
main_menu.addMenu(submenu2)
submenu1.addAction(QAction("SubItem 1.1", submenu1))
submenu1.addAction(QAction("SubItem 1.2", submenu1))
submenu2.addAction(QAction("SubItem 2.1", submenu2))
submenu2_submenu = QMenu("SubSubmenu")
submenu2.addMenu(submenu2_submenu)
submenu2_submenu.addAction(QAction("SubSubItem 2.1.1", submenu2_submenu))

result = h.pyside.generate_markdown_from_qmenu(main_menu)
print(*result, sep="\n")
# - Item 1
# - **Submenu 1**
#   - SubItem 1.1
#   - SubItem 1.2
# - Item 2
# - **Submenu 2**
#   - SubItem 2.1
#   - **SubSubmenu**
#     - SubSubItem 2.1.1
```

<details>
<summary>Code:</summary>

```python
def generate_markdown_from_qmenu(menu: QMenu, level: int = 0) -> List[str]:
    markdown_lines: List[str] = []
    for action in menu.actions():
        if action.menu():  # If the action has a submenu
            # Add a header for the submenu
            markdown_lines.append(f"{'  ' * level}- **{action.text()}**")
            # Recursively traverse the submenu
            markdown_lines.extend(generate_markdown_from_qmenu(action.menu(), level + 1))
        else:
            # Add a regular menu item
            if action.text():
                markdown_lines.append(f"{'  ' * level}- {action.text()}")
    return markdown_lines
```

</details>
