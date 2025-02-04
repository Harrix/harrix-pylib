from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import harrix_pylib as h


def test_add_diary_new_diary():
    with TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        # Define the YAML header for the Markdown note
        beginning_of_md = """---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: ru
---
"""

        # Test with images
        is_with_images = True

        result_msg, result_path = h.md.add_diary_new_diary(base_path, beginning_of_md, is_with_images)

        # Check if the message indicates file creation
        assert "File" in result_msg

        # Extract the date components from the result path for testing
        current_date = datetime.now()
        year = current_date.strftime("%Y")
        month = current_date.strftime("%m")
        day = current_date.strftime("%Y-%m-%d")

        # Check if the diary structure is created correctly
        diary_year_path = base_path / year
        assert diary_year_path.is_dir()

        diary_month_path = diary_year_path / month
        assert diary_month_path.is_dir()

        # Check if the diary file exists in the correct location
        diary_file = diary_month_path / f"{day}/{day}.md"
        assert diary_file.is_file()

        # Check if the image folder was created
        img_folder = diary_month_path / f"{day}/img"
        assert img_folder.is_dir()

        # Verify content of the diary file
        with diary_file.open("r", encoding="utf-8") as file:
            content = file.read()
            assert beginning_of_md in content
            assert f"# {day}\n\n" in content
            assert f"## {datetime.now().strftime('%H:%M')}\n\n" in content

        # Test without images
        is_with_images = False

        result_msg, result_path = h.md.add_diary_new_diary(base_path, beginning_of_md, is_with_images)

        # Check if the message indicates file creation
        assert "File" in result_msg

        # Verify that the new diary entry is added to the existing diary structure
        new_diary_file = diary_month_path / f"{day}.md"
        assert new_diary_file.is_file()

        # Verify content of the new diary file
        with new_diary_file.open("r", encoding="utf-8") as file:
            content = file.read()
            assert beginning_of_md in content
            assert f"# {day}\n\n" in content
            assert f"## {datetime.now().strftime('%H:%M')}\n\n" in content


def test_add_diary_new_dream():
    with TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        # Define the YAML header for the Markdown note
        beginning_of_md = """---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: ru
---
"""

        # Test with images
        is_with_images = True

        result_msg, result_path = h.md.add_diary_new_dream(base_path, beginning_of_md, is_with_images)

        # Check if the message indicates file creation
        assert "File" in result_msg

        # Extract the date components from the result path for testing
        current_date = datetime.now()
        year = current_date.strftime("%Y")
        month = current_date.strftime("%m")
        day = current_date.strftime("%Y-%m-%d")

        # Check if the diary structure is created correctly
        diary_year_path = base_path / year
        assert diary_year_path.is_dir()

        diary_month_path = diary_year_path / month
        assert diary_month_path.is_dir()

        # Check if the dream diary file exists in the correct location
        dream_diary_file = diary_month_path / f"{day}/{day}.md"
        assert dream_diary_file.is_file()

        # Check if the image folder was created
        img_folder = diary_month_path / f"{day}/img"
        assert img_folder.is_dir()

        # Verify content of the dream diary file
        with dream_diary_file.open("r", encoding="utf-8") as file:
            content = file.read()
            assert beginning_of_md in content
            assert f"# {day}" in content
            assert f"## {datetime.now().strftime('%H:%M')}" in content
            assert content.count("`` — не помню.\n") == 16

        # Test without images
        is_with_images = False

        result_msg, result_path = h.md.add_diary_new_dream(base_path, beginning_of_md, is_with_images)

        # Check if the message indicates file creation
        assert "File" in result_msg

        # Verify that the new dream diary file is added to the existing diary structure
        new_dream_diary_file = diary_month_path / f"{day}.md"
        assert new_dream_diary_file.is_file()

        # Verify content of the new dream diary file
        with new_dream_diary_file.open("r", encoding="utf-8") as file:
            content = file.read()
            assert beginning_of_md in content
            assert f"# {day}" in content
            assert f"## {datetime.now().strftime('%H:%M')}" in content
            assert content.count("`` — не помню.\n") == 16


def test_add_diary_new_note():
    with TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        # Test without images
        text = "# Diary Entry\nThis is a diary test entry without images."
        is_with_images = False

        result_msg, result_path = h.md.add_diary_new_note(base_path, text, is_with_images)

        # Check if the message indicates file creation
        assert "File" in result_msg

        # Extract the date components from the result path for testing
        current_date = datetime.now()
        year = current_date.strftime("%Y")
        month = current_date.strftime("%m")
        day = current_date.strftime("%Y-%m-%d")

        # Check if the diary structure is created correctly
        diary_year_path = base_path / year
        assert diary_year_path.is_dir()

        diary_month_path = diary_year_path / month
        assert diary_month_path.is_dir()

        # Check if the note file exists in the correct location
        note_file = diary_month_path / f"{day}.md"
        assert note_file.is_file()

        # Verify content of the note file
        with note_file.open("r", encoding="utf-8") as file:
            assert file.read().strip() == text

        # Test with images
        text = "# Diary Entry\nThis is a diary test entry with images."
        is_with_images = True

        result_msg, result_path = h.md.add_diary_new_note(base_path, text, is_with_images)

        # Check if the message indicates file creation
        assert "File" in result_msg

        # Verify that the new note is added to the existing diary structure
        note_file = diary_month_path / f"{day}/{day}.md"
        assert note_file.is_file()

        # Verify content of the new note file
        with note_file.open("r", encoding="utf-8") as file:
            assert file.read().strip() == text

        # Check that there's image folder created for the second entry
        assert (diary_month_path / f"{day}/img").exists()


def test_add_note():
    with TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        # Test with images
        name = "test_note"
        text = "# Test Note\nThis is a test note with images."
        is_with_images = True

        result_msg, result_path = h.md.add_note(base_path, name, text, is_with_images)

        # Check if the message indicates file creation
        assert "File" in result_msg

        # Check if the note file exists
        note_file = base_path / f"{name}/{name}.md"
        assert note_file.is_file()

        # Check if the image folder was created
        img_folder = base_path / f"{name}/img"
        assert img_folder.is_dir()

        # Verify content of the note file
        with note_file.open("r", encoding="utf-8") as file:
            assert file.read().strip() == text

        # Test without images
        name = "test_note_no_images"
        text = "# Simple Note\nThis note has no images."
        is_with_images = False

        result_msg, result_path = h.md.add_note(base_path, name, text, is_with_images)

        # Check if the message indicates file creation
        assert "File" in result_msg

        # Check if the note file exists at the base path
        note_file_no_images = base_path / f"{name}.md"
        assert note_file_no_images.is_file()

        # Verify content of the note file
        with note_file_no_images.open("r", encoding="utf-8") as file:
            assert file.read().strip() == text

        # Check that there's no image folder created
        assert not (base_path / f"{name}/img").exists()


def test_format_yaml():
    current_folder = h.dev.get_project_root()
    md = Path(current_folder / "tests/data/format_yaml__before.md").read_text(encoding="utf8")
    md_after = Path(current_folder / "tests/data/format_yaml__after.md").read_text(encoding="utf8")

    with TemporaryDirectory() as temp_folder:
        temp_filename = Path(temp_folder) / "temp.md"
        temp_filename.write_text(md, encoding="utf-8")
        h.md.format_yaml(temp_filename)
        md_applied = temp_filename.read_text(encoding="utf8")

    assert md_after == md_applied


def test_generate_author_book():
    current_folder = h.dev.get_project_root()
    md = Path(current_folder / "tests/data/generate_author_book__before.md").read_text(encoding="utf8")
    md_after = Path(current_folder / "tests/data/generate_author_book__after.md").read_text(encoding="utf8")

    with TemporaryDirectory() as temp_folder:
        temp_filename = Path(temp_folder) / "temp.md"
        temp_filename.write_text(md, encoding="utf-8")
        h.md.generate_author_book(temp_filename)
        md_applied = temp_filename.read_text(encoding="utf8")
        md_after = md_after.replace("Name Surname", Path(temp_folder).name)

    assert md_after == md_applied


def test_generate_image_captions():
    current_folder = h.dev.get_project_root()
    md = Path(current_folder / "tests/data/generate_image_captions__before.md").read_text(encoding="utf8")
    md_after = Path(current_folder / "tests/data/generate_image_captions__after.md").read_text(encoding="utf8")

    with TemporaryDirectory() as temp_folder:
        temp_filename = Path(temp_folder) / "temp.md"
        temp_filename.write_text(md, encoding="utf-8")
        h.md.generate_image_captions(temp_filename)
        md_applied = temp_filename.read_text(encoding="utf8")

    assert md_after == md_applied


def test_generate_toc_with_links():
    current_folder = h.dev.get_project_root()
    md = Path(current_folder / "tests/data/generate_toc_with_links__before.md").read_text(encoding="utf8")
    md_after = Path(current_folder / "tests/data/generate_toc_with_links__after.md").read_text(encoding="utf8")

    with TemporaryDirectory() as temp_folder:
        temp_filename = Path(temp_folder) / "temp.md"
        temp_filename.write_text(md, encoding="utf-8")
        h.md.generate_toc_with_links(temp_filename)
        md_applied = temp_filename.read_text(encoding="utf8")

    assert md_after == md_applied


def test_get_yaml_content():
    md = Path(h.dev.get_project_root() / "tests/data/get_yaml_content.md").read_text(encoding="utf8")
    yaml = h.md.get_yaml_content(md)
    assert len(yaml.splitlines()) == 4


def test_identify_code_blocks():
    md = Path(h.dev.get_project_root() / "tests/data/generate_image_captions__before.md").read_text(encoding="utf8")
    _, content = h.md.split_yaml_content(md)
    count_lines_content = 0
    count_lines_code = 0
    for _, state in h.md.identify_code_blocks(content.splitlines()):
        if state:
            count_lines_code += 1
        else:
            count_lines_content += 1
    assert count_lines_code == 9
    assert count_lines_content == 22


def test_remove_yaml_content():
    md = Path(h.dev.get_project_root() / "tests/data/get_yaml_content.md").read_text(encoding="utf8")
    md_clean = h.md.remove_yaml_content(md)
    assert len(md_clean.splitlines()) == 1


def test_remove_yaml_and_code_content():
    md = Path(h.dev.get_project_root() / "tests/data/remove_yaml_and_code_content.md").read_text(encoding="utf8")
    md_clean = h.md.remove_yaml_and_code_content(md)
    assert len(md_clean.splitlines()) == 26


def test_replace_section():
    with TemporaryDirectory() as temp_dir:
        # Create a test file with some content
        test_file_path = Path(temp_dir) / "testfile.md"
        original_content = """# Header

Some content here

## List of commands

- command1

###  Subsection

- command2

## Footer

More content here
"""
        with open(test_file_path, "w", encoding="utf-8") as file:
            file.write(original_content)

        # New content to replace the section
        new_content = "New list of commands:\n\n- new command1\n- new command2"

        # Call the function to replace the section
        result_message = h.md.replace_section(test_file_path, new_content)

        print(result_message)

        # Check if the function returns the expected message
        assert result_message == "Section ## List of commands is replaced.", (
            "The message does not match the expected result"
        )

        # Read the modified file content
        with open(test_file_path, "r", encoding="utf-8") as file:
            updated_content = file.read()

        # Expected content after replacement
        expected_content = """# Header

Some content here

## List of commands

New list of commands:

- new command1
- new command2

## Footer

More content here
"""

        # Ensure the content was updated as expected
        assert updated_content == expected_content, "The file content was not updated correctly"

        original_content = """# Header

Some content here

## List of commands

- command1

###  Subsection

- command2

### Footer

More content here

#### Sub

Text.
"""
        with open(test_file_path, "w", encoding="utf-8") as file:
            file.write(original_content)

        # New content to replace the section
        new_content = "New list of commands:\n\n- new command1\n- new command2"

        # Call the function to replace the section
        result_message = h.md.replace_section(test_file_path, new_content, "### Footer")

        print(result_message)

        # Check if the function returns the expected message
        assert result_message == "Section ### Footer is replaced.", "The message does not match the expected result"

        # Read the modified file content
        with open(test_file_path, "r", encoding="utf-8") as file:
            updated_content = file.read()

        # Expected content after replacement
        expected_content = """# Header

Some content here

## List of commands

- command1

###  Subsection

- command2

### Footer

New list of commands:

- new command1
- new command2

"""

        # Ensure the content was updated as expected
        assert updated_content == expected_content, "The file content was not updated correctly"


def test_sort_sections():
    current_folder = h.dev.get_project_root()
    md = Path(current_folder / "tests/data/sort_sections__before.md").read_text(encoding="utf8")
    md_after = Path(current_folder / "tests/data/sort_sections__after.md").read_text(encoding="utf8")

    with TemporaryDirectory() as temp_folder:
        temp_filename = Path(temp_folder) / "temp.md"
        temp_filename.write_text(md, encoding="utf-8")
        h.md.sort_sections(temp_filename)
        md_applied = temp_filename.read_text(encoding="utf8")

    assert md_after == md_applied


def test_split_yaml_content():
    md = Path(h.dev.get_project_root() / "tests/data/get_yaml_content.md").read_text(encoding="utf8")
    yaml, content = h.md.split_yaml_content(md)
    assert len(yaml.splitlines()) + len(content.splitlines()) == 5
