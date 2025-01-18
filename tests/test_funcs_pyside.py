import pytest
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu

import harrix_pylib as h


@pytest.fixture(scope="session")
def fixture_q_application():
    app = QApplication([])
    yield app
    app.quit()


def test_create_emoji_icon(fixture_q_application):
    # Test with default size
    emoji = "😊"
    icon = h.pyside.create_emoji_icon(emoji)
    assert isinstance(icon, QIcon)

    # Verify the pixmap properties
    pixmap = icon.pixmap(32, 32)  # Assuming the default size is 32x32

    # Check if pixmap is not null
    assert not pixmap.isNull()

    # Check pixmap size
    assert pixmap.width() == 32
    assert pixmap.height() == 32

    # Check for transparency (this is a bit tricky due to the nature of emojis)
    # Here we check if there are transparent pixels around the emoji
    has_transparent_border = any(
        pixmap.toImage().pixelColor(x, y).alpha() == 0
        for x in range(pixmap.width())
        for y in (0, pixmap.height() - 1)  # Top and bottom row
    ) or any(
        pixmap.toImage().pixelColor(x, y).alpha() == 0
        for y in range(pixmap.height())
        for x in (0, pixmap.width() - 1)  # Left and right column
    )
    assert has_transparent_border

    # Test with different size
    size = 64
    icon = h.pyside.create_emoji_icon(emoji, size)
    pixmap = icon.pixmap(size, size)
    assert pixmap.width() == size
    assert pixmap.height() == size

    # Test with a different emoji to ensure the function handles various emojis
    different_emoji = "🚀"
    icon = h.pyside.create_emoji_icon(different_emoji)
    pixmap = icon.pixmap(32, 32)
    assert not pixmap.isNull()


def test_generate_markdown_from_qmenu(fixture_q_application):
    # Create a mock QMenu structure
    main_menu = QMenu("Main Menu")
    submenu1 = QMenu("Submenu 1")
    submenu2 = QMenu("Submenu 2")

    # Adding actions and submenus to main_menu
    main_menu.addAction(QAction("Item 1", main_menu))
    main_menu.addMenu(submenu1)
    main_menu.addAction(QAction("Item 2", main_menu))
    main_menu.addMenu(submenu2)

    # Adding actions to submenus
    submenu1.addAction(QAction("SubItem 1.1", submenu1))
    submenu1.addAction(QAction("SubItem 1.2", submenu1))

    submenu2.addAction(QAction("SubItem 2.1", submenu2))
    submenu2_submenu = QMenu("SubSubmenu")
    submenu2.addMenu(submenu2_submenu)
    submenu2_submenu.addAction(QAction("SubSubItem 2.1.1", submenu2_submenu))

    # Generate markdown
    result = h.pyside.generate_markdown_from_qmenu(main_menu)

    # Expected markdown output
    expected = [
        "- Item 1",
        "- **Submenu 1**",
        "  - SubItem 1.1",
        "  - SubItem 1.2",
        "- Item 2",
        "- **Submenu 2**",
        "  - SubItem 2.1",
        "  - **SubSubmenu**",
        "    - SubSubItem 2.1.1",
    ]

    # Assert that the markdown matches the expected output
    assert result == expected, f"Expected {expected}, but got {result}"
