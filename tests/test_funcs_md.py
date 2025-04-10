from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

import harrix_pylib as h


def test_add_diary_entry_in_year():
    # Test setup
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        front_matter = "---\ntitle: Test Diary\n---\n"

        # Test 1: Basic add_diary_entry_in_year with a new file
        entry_content = "This is a test entry.\n\n"
        message, file_path = h.md.add_diary_entry_in_year(temp_path, front_matter, entry_content)

        # Assertions for Test 1
        current_year = datetime.now().strftime("%Y")
        expected_file_path = temp_path / f"{current_year}.md"
        assert file_path == expected_file_path
        assert expected_file_path.exists()
        assert "created" in message

        # Read the file content to verify structure
        content = expected_file_path.read_text(encoding="utf-8")
        assert front_matter in content
        assert f"# {current_year}" in content
        assert "<details>" in content
        assert "<summary>📖 Contents</summary>" in content
        assert "## Contents" in content
        assert "</details>" in content

        # Check entry format
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M")
        assert f"## {current_date}" in content
        assert f"### {current_time}" in content
        assert entry_content in content

        # Test 2: Add another entry to the existing file
        second_entry = "This is a second test entry.\n\n"
        message2, file_path2 = h.md.add_diary_entry_in_year(temp_path, front_matter, second_entry)

        # Assertions for Test 2
        assert file_path2 == expected_file_path
        assert "updated" in message2

        # Read the updated content
        updated_content = expected_file_path.read_text(encoding="utf-8")
        assert second_entry in updated_content
        assert updated_content.count(f"## {current_date}") == 2  # Two entries for the same date


def test_add_diary_new_dairy_in_year():
    # Test setup
    with TemporaryDirectory() as temp_dir:
        front_matter = "---\ntitle: Test Diary\n---\n"

        # Assertions for Test 1
        current_year = datetime.now().strftime("%Y")

        # Test 1: Test add_diary_new_dairy_in_year
        # Create a new temporary directory to test with a fresh file
        with TemporaryDirectory() as temp_dir2:
            temp_path2 = Path(temp_dir2)
            dairy_message, dairy_file_path = h.md.add_diary_new_dairy_in_year(temp_path2, front_matter)

            # Assertions for Test 4
            expected_dairy_path = temp_path2 / f"{current_year}.md"
            assert dairy_file_path == expected_dairy_path
            assert expected_dairy_path.exists()
            assert "created" in dairy_message

            # Read the content
            dairy_content = expected_dairy_path.read_text(encoding="utf-8")
            assert "Text." in dairy_content


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
            assert content.count("`` — I don't remember.\n") == 16

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
            assert content.count("`` — I don't remember.\n") == 16


def test_add_diary_new_dream_in_year():
    # Test setup
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        front_matter = "---\ntitle: Test Diary\n---\n"

        current_year = datetime.now().strftime("%Y")
        expected_file_path = temp_path / f"{current_year}.md"

        # Test 1: Test add_diary_new_dream_in_year
        _, dream_file_path = h.md.add_diary_new_dream_in_year(temp_path, front_matter)

        # Assertions for Test 3
        assert dream_file_path == expected_file_path

        # Read the updated content
        dream_content = expected_file_path.read_text(encoding="utf-8")
        assert "`` — I don't remember." in dream_content
        # Check that it contains the placeholder text repeated 16 times
        assert dream_content.count("`` — I don't remember.") == 16

        # Test 2: Test add_diary_new_dairy_in_year
        # Create a new temporary directory to test with a fresh file
        with TemporaryDirectory() as temp_dir2:
            temp_path2 = Path(temp_dir2)
            dairy_message, dairy_file_path = h.md.add_diary_new_dairy_in_year(temp_path2, front_matter)

            # Assertions for Test 4
            expected_dairy_path = temp_path2 / f"{current_year}.md"
            assert dairy_file_path == expected_dairy_path
            assert expected_dairy_path.exists()
            assert "created" in dairy_message

            # Read the content
            dairy_content = expected_dairy_path.read_text(encoding="utf-8")
            assert "Text." in dairy_content


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


def test_append_path_to_local_links_images_line():
    with TemporaryDirectory() as temp_dir:
        adding_path = temp_dir.replace("\\", "/")

        # Test case for image
        markdown_line = "Here is an ![image](image.jpg)"
        expected_result = f"Here is an ![image]({adding_path}/image.jpg)"
        assert h.md.append_path_to_local_links_images_line(markdown_line, adding_path) == expected_result

        # Test case for link
        markdown_line = "Here is a [link](folder/link.md)"
        expected_result = f"Here is a [link]({adding_path}/folder/link.md)"
        assert h.md.append_path_to_local_links_images_line(markdown_line, adding_path) == expected_result

        # Test case with Windows-style backslashes
        markdown_line = "Here is an ![image](image\\with\\backslashes.jpg)"
        expected_result = f"Here is an ![image]({adding_path}/image/with/backslashes.jpg)"
        assert h.md.append_path_to_local_links_images_line(markdown_line, adding_path) == expected_result

        # Test case to ensure external links are not modified
        markdown_line = "Here is a [link](https://example.com)"
        expected_result = "Here is a [link](https://example.com)"
        assert h.md.append_path_to_local_links_images_line(markdown_line, adding_path) == expected_result

        # Test case with multiple links in one line
        markdown_line = "Here is an ![image](image.jpg) and a [link](folder/link.md)"
        expected_result = f"Here is an ![image]({adding_path}/image.jpg) and a [link]({adding_path}/folder/link.md)"
        assert h.md.append_path_to_local_links_images_line(markdown_line, adding_path) == expected_result

        # Test case to ensure trailing slash in adding_path is removed
        adding_path_with_slash = f"{adding_path}/"
        markdown_line = "Here is an ![image](image.jpg)"
        expected_result = f"Here is an ![image]({adding_path}/image.jpg)"
        assert h.md.append_path_to_local_links_images_line(markdown_line, adding_path_with_slash) == expected_result

        # Test case with no links
        markdown_line = "No links here"
        assert h.md.append_path_to_local_links_images_line(markdown_line, adding_path) == "No links here"


def test_combine_markdown_files():
    with TemporaryDirectory() as temp_dir:
        # Create test files
        folder_path = Path(temp_dir)

        # Create a test markdown file
        file1_content = """---
title: Test File 1
tags: [python, test]
---
# Test Content
This is test content."""

        (folder_path / "file1.md").write_text(file1_content, encoding="utf-8")

        # Create a file that should be skipped due to published: false
        file2_content = """---
title: Test File 2
published: false
---
# Should be skipped
This content should not appear in the final file."""

        (folder_path / "file2.md").write_text(file2_content, encoding="utf-8")

        # Call the function
        result = h.md.combine_markdown_files(folder_path)

        # Check the result message
        assert "✅ File" in result
        assert ".g.md is created" in result

        # Check the created file
        output_file = folder_path / f"_{folder_path.name}.g.md"
        assert output_file.exists()

        # Read the content
        content = output_file.read_text(encoding="utf-8")

        # Check that YAML header was processed
        assert "title: Test File 1" in content
        assert "tags:" in content
        assert "python" in content
        assert "test" in content

        # Check that content was included
        assert "# Test Content" in content or "## Test Content" in content
        assert "This is test content" in content

        # Check that the file with published: false was skipped
        assert "Should be skipped" not in content


def test_combine_markdown_files_recursively():
    with TemporaryDirectory() as temp_dir:
        root_path = Path(temp_dir)

        # Create a test folder structure
        # Root
        # ├── folder1
        # │   ├── file1.md
        # │   └── file2.md
        # ├── folder2
        # │   ├── file3.md
        # │   └── subfolder1
        # │       └── file4.md
        # ├── folder3
        # │   └── file5.md
        # ├── .hidden_folder
        # │   └── hidden_file.md
        # └── existing.g.md

        # Create folders
        folder1 = root_path / "folder1"
        folder2 = root_path / "folder2"
        folder3 = root_path / "folder3"
        subfolder1 = folder2 / "subfolder1"
        hidden_folder = root_path / ".hidden_folder"

        for folder in [folder1, folder2, folder3, subfolder1, hidden_folder]:
            folder.mkdir()

        # Create markdown files
        (folder1 / "file1.md").write_text("# File 1")
        (folder1 / "file2.md").write_text("# File 2")
        (folder2 / "file3.md").write_text("# File 3")
        (subfolder1 / "file4.md").write_text("# File 4")
        (folder3 / "file5.md").write_text("# File 5")
        (hidden_folder / "hidden_file.md").write_text("# Hidden File")

        # Create an existing .g.md file that should be deleted
        (root_path / "existing.g.md").write_text("# Existing Generated File")

        # Call the function being tested
        h.md.combine_markdown_files_recursively(root_path)

        # Verify existing .g.md file was deleted
        assert not (root_path / "existing.g.md").exists()

        # Check which folders were processed (by checking for generated files)
        assert (folder1 / f"_{folder1.name}.g.md").exists()  # folder1 has 2 files directly
        assert (folder2 / f"_{folder2.name}.g.md").exists()  # folder2 has 1 file + 1 in subfolder

        # folder3 should not be processed (only 1 file)
        assert not (folder3 / f"_{folder3.name}.g.md").exists()

        # .hidden_folder should be skipped
        assert not (hidden_folder / f"_{hidden_folder.name}.g.md").exists()


@pytest.mark.slow
def test_download_and_replace_images():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        md_file = temp_path / "test.md"
        md_file.write_text("![Test Image](https://picsum.photos/200/300.png)")
        h.md.download_and_replace_images(md_file)
        assert "![Test Image](300.png)" not in md_file.read_text()


@pytest.mark.slow
def test_download_and_replace_images_content():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        md_file = temp_path / "test.md"
        md_file.write_text("![Test Image](https://picsum.photos/200/300.png)")
        updated_text = h.md.download_and_replace_images_content(md_file.read_text(), temp_dir, image_folder="img")
        assert "![Test Image](300.png)" not in updated_text


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


def test_format_yaml_content():
    current_folder = h.dev.get_project_root()
    md = Path(current_folder / "tests/data/format_yaml__before.md").read_text(encoding="utf8")
    md_after = Path(current_folder / "tests/data/format_yaml__after.md").read_text(encoding="utf8")

    assert md_after == h.md.format_yaml_content(md)


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


def test_generate_image_captions_content():
    current_folder = h.dev.get_project_root()
    md = Path(current_folder / "tests/data/generate_image_captions__before.md").read_text(encoding="utf8")
    md_after = Path(current_folder / "tests/data/generate_image_captions__after.md").read_text(encoding="utf8")
    assert md_after == h.md.generate_image_captions_content(md)


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


def test_generate_toc_with_links_content():
    current_folder = h.dev.get_project_root()
    md = Path(current_folder / "tests/data/generate_toc_with_links__before.md").read_text(encoding="utf8")
    md_after = Path(current_folder / "tests/data/generate_toc_with_links__after.md").read_text(encoding="utf8")
    assert md_after == h.md.generate_toc_with_links_content(md)


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


def test_identify_code_blocks_line():
    test_cases = [
        ("No code here", [("No code here", False)]),
        ("`code` within text", [("`code`", True), (" within text", False)]),
        ("Before `code` and after", [("Before ", False), ("`code`", True), (" and after", False)]),
        ("`backtick` alone", [("`backtick`", True), (" alone", False)]),
        ("```triple backticks```", [("```triple backticks```", True)]),
        ("``double backticks``", [("``double backticks``", True)]),
        ("Mixed `code` and ``double``", [("Mixed ", False), ("`code`", True), (" and ", False), ("``double``", True)]),
    ]

    for markdown_line, expected in test_cases:
        result = list(h.md.identify_code_blocks_line(markdown_line))
        assert result == expected, f"Failed for: {markdown_line}"


def test_increase_heading_level_content():
    md_text = """# Heading
This is some text.

## Subheading
More text here."""

    expected = """## Heading
This is some text.

### Subheading
More text here."""
    assert h.md.increase_heading_level_content(md_text) == expected


def test_remove_toc_content():
    current_folder = h.dev.get_project_root()
    md = Path(current_folder / "tests/data/generate_toc_with_links__after.md").read_text(encoding="utf8")
    md_after = Path(current_folder / "tests/data/generate_toc_with_links__before.md").read_text(encoding="utf8")
    assert md_after == h.md.remove_toc_content(md)


def test_remove_yaml_and_code_content():
    md = Path(h.dev.get_project_root() / "tests/data/remove_yaml_and_code_content.md").read_text(encoding="utf8")
    md_clean = h.md.remove_yaml_and_code_content(md)
    assert len(md_clean.splitlines()) == 26


def test_remove_yaml_content():
    md = Path(h.dev.get_project_root() / "tests/data/get_yaml_content.md").read_text(encoding="utf8")
    md_clean = h.md.remove_yaml_content(md)
    assert len(md_clean.splitlines()) == 1


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
        h.md.replace_section(test_file_path, new_content)

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
        h.md.replace_section(test_file_path, new_content, "### Footer")

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


def test_replace_section_content():
    original_content = """# Header

Some content here

## List of commands

- command1

###  Subsection

- command2

## Footer

More content here
"""

    # New content to replace the section
    new_content = "New list of commands:\n\n- new command1\n- new command2"

    # Call the function to replace the section
    updated_content = h.md.replace_section_content(original_content, new_content)

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

    # New content to replace the section
    new_content = "New list of commands:\n\n- new command1\n- new command2"

    # Call the function to replace the section
    updated_content = h.md.replace_section_content(original_content, new_content, "### Footer")

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


def test_sort_sections_content():
    current_folder = h.dev.get_project_root()
    md = Path(current_folder / "tests/data/sort_sections__before.md").read_text(encoding="utf8")
    md_after = Path(current_folder / "tests/data/sort_sections__after.md").read_text(encoding="utf8")
    md_applied = h.md.sort_sections_content(md)
    assert md_after == md_applied


def test_split_toc_content_basic():
    markdown = (
        "# Title\n\n"
        "- [Introduction](#introduction)\n"
        "- [Content](#content)\n\n"
        "## Introduction\n\n"
        "This is the start.\n\n"
        "## Content\n\n"
        "This is the content."
    )

    expected_toc = "- [Introduction](#introduction)\n- [Content](#content)"

    expected_content = "# Title\n\n## Introduction\n\nThis is the start.\n\n## Content\n\nThis is the content."

    toc, content = h.md.split_toc_content(markdown)
    assert toc == expected_toc
    assert content == expected_content

    markdown = (
        "---\n"
        "title: My Document\n"
        "author: John Doe\n"
        "---\n"
        "# Title\n\n"
        "- [Introduction](#introduction)\n"
        "- [Content](#content)\n\n"
        "## Introduction\n\n"
        "This is the start.\n\n"
        "## Content\n\n"
        "This is the content."
    )

    expected_toc = "- [Introduction](#introduction)\n- [Content](#content)"

    expected_content = "# Title\n\n## Introduction\n\nThis is the start.\n\n## Content\n\nThis is the content."

    toc, content = h.md.split_toc_content(markdown)
    assert toc == expected_toc
    assert content == expected_content


def test_split_yaml_content():
    md = Path(h.dev.get_project_root() / "tests/data/get_yaml_content.md").read_text(encoding="utf8")
    yaml, content = h.md.split_yaml_content(md)
    assert len(yaml.splitlines()) + len(content.splitlines()) == 5
