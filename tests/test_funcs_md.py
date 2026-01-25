"""Tests for the functions in the md module of harrix_pylib."""

import re
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

import harrix_pylib as h


def test_add_diary_entry_in_year() -> None:
    # Test setup
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        front_matter = "---\ntitle: Test Diary\n---\n"

        # Test 1: Basic add_diary_entry_in_year with a new file
        entry_content = "This is a test entry.\n\n"
        message, file_path = h.md.add_diary_entry_in_year(temp_path, front_matter, entry_content)

        # Assertions for Test 1
        current_year = datetime.now(UTC).strftime("%Y")
        expected_file_path = temp_path / f"{current_year}.md"
        assert file_path == expected_file_path
        assert expected_file_path.exists()
        assert "created" in message

        # Read the file content to verify structure
        content = expected_file_path.read_text(encoding="utf-8")
        assert front_matter in content
        assert f"# {current_year}" in content
        assert "<details>" in content
        assert "<summary>📖 Contents ⬇️</summary>" in content
        assert "## Contents" in content
        assert "</details>" in content

        # Check entry format
        current_date = datetime.now(UTC).strftime("%Y-%m-%d")
        current_time = datetime.now(UTC).strftime("%H:%M")
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
        count_entries = 2
        assert updated_content.count(f"## {current_date}") == count_entries  # Two entries for the same date


def test_add_diary_new_dairy_in_year() -> None:
    # Test setup
    front_matter = "---\ntitle: Test Diary\n---\n"

    # Assertions for Test 1
    current_year = datetime.now(UTC).strftime("%Y")

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


def test_add_diary_new_diary() -> None:
    with TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        # Define the YAML header for the Markdown note
        beginning_of_md = """---
author: Jane Doe
author-email: jane.doe@example.com
lang: ru
---
"""

        # Test with images
        is_with_images = True

        result_msg, _ = h.md.add_diary_new_diary(base_path, beginning_of_md, is_with_images=is_with_images)

        # Check if the message indicates file creation
        assert "File" in result_msg

        # Extract the date components from the result path for testing
        current_date = datetime.now(UTC)
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
            assert f"## {datetime.now(UTC).strftime('%H:%M')}\n\n" in content

        # Test without images
        is_with_images = False

        result_msg, _ = h.md.add_diary_new_diary(base_path, beginning_of_md, is_with_images=is_with_images)

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
            assert f"## {datetime.now(UTC).strftime('%H:%M')}\n\n" in content


def test_add_diary_new_dream() -> None:
    with TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        # Define the YAML header for the Markdown note
        beginning_of_md = """---
author: Jane Doe
author-email: jane.doe@example.com
lang: ru
---
"""

        # Test with images
        is_with_images = True

        result_msg, _ = h.md.add_diary_new_dream(base_path, beginning_of_md, is_with_images=is_with_images)

        # Check if the message indicates file creation
        assert "File" in result_msg

        # Extract the date components from the result path for testing
        current_date = datetime.now(UTC)
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
            assert f"## {datetime.now(UTC).strftime('%H:%M')}" in content
            count_i_dont_remember = 16
            assert content.count("`` — I don't remember.\n") == count_i_dont_remember

        # Test without images
        is_with_images = False

        result_msg, _ = h.md.add_diary_new_dream(base_path, beginning_of_md, is_with_images=is_with_images)

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
            assert f"## {datetime.now(UTC).strftime('%H:%M')}" in content
            count_i_dont_remember = 16
            assert content.count("`` — I don't remember.\n") == count_i_dont_remember


def test_add_diary_new_dream_in_year() -> None:
    # Test setup
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        front_matter = "---\ntitle: Test Diary\n---\n"

        current_year = datetime.now(UTC).strftime("%Y")
        expected_file_path = temp_path / f"{current_year}.md"

        # Test 1: Test add_diary_new_dream_in_year
        _, dream_file_path = h.md.add_diary_new_dream_in_year(temp_path, front_matter)

        # Assertions for Test 3
        assert dream_file_path == expected_file_path

        # Read the updated content
        dream_content = expected_file_path.read_text(encoding="utf-8")
        assert "`` — I don't remember." in dream_content
        # Check that it contains the placeholder text repeated 16 times
        count_i_dnt_remember = 16
        assert dream_content.count("`` — I don't remember.") == count_i_dnt_remember

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


def test_add_diary_new_note() -> None:
    with TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        # Test without images
        text = "# Diary Entry\nThis is a diary test entry without images."
        is_with_images = False

        result_msg, _ = h.md.add_diary_new_note(base_path, text, is_with_images=is_with_images)

        # Check if the message indicates file creation
        assert "File" in result_msg

        # Extract the date components from the result path for testing
        current_date = datetime.now(UTC)
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

        result_msg, _ = h.md.add_diary_new_note(base_path, text, is_with_images=is_with_images)

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


def test_add_note() -> None:
    with TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        # Test with images
        name = "test_note"
        text = "# Test Note\nThis is a test note with images."
        is_with_images = True

        result_msg, _ = h.md.add_note(base_path, name, text, is_with_images=is_with_images)

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

        result_msg, _ = h.md.add_note(base_path, name, text, is_with_images=is_with_images)

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


def test_append_path_to_local_links_images_line() -> None:
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


def test_combine_markdown_files() -> None:
    with TemporaryDirectory() as temp_dir:
        # Create test files
        folder_path = Path(temp_dir)

        # Create a test Markdown file
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


def test_combine_markdown_files_recursively() -> None:
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

        # Create Markdown files
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


def test_delete_g_md_files_recursively() -> None:
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test directory structure
        (temp_path / "subfolder1").mkdir()
        (temp_path / "subfolder2").mkdir()
        (temp_path / ".hidden_folder").mkdir()
        (temp_path / "subfolder1" / "nested").mkdir()

        # Create various files
        (temp_path / "file1.g.md").write_text("content")
        (temp_path / "file2.md").write_text("content")
        (temp_path / "file3.txt").write_text("content")
        (temp_path / "subfolder1" / "file4.g.md").write_text("content")
        (temp_path / "subfolder1" / "file5.md").write_text("content")
        (temp_path / "subfolder2" / "file6.g.md").write_text("content")
        (temp_path / ".hidden_folder" / "file7.g.md").write_text("content")
        (temp_path / "subfolder1" / "nested" / "file8.g.md").write_text("content")

        # Verify initial state
        assert (temp_path / "file1.g.md").exists()
        assert (temp_path / "file2.md").exists()
        assert (temp_path / "file3.txt").exists()
        assert (temp_path / "subfolder1" / "file4.g.md").exists()
        assert (temp_path / "subfolder1" / "file5.md").exists()
        assert (temp_path / "subfolder2" / "file6.g.md").exists()
        assert (temp_path / ".hidden_folder" / "file7.g.md").exists()
        assert (temp_path / "subfolder1" / "nested" / "file8.g.md").exists()

        # Run the function
        result = h.md.delete_g_md_files_recursively(temp_path)

        # Verify result message
        assert result == "✅ Files `*.g.md` deleted"

        # Verify that *.g.md files are deleted (except in hidden folders)
        assert not (temp_path / "file1.g.md").exists()
        assert not (temp_path / "subfolder1" / "file4.g.md").exists()
        assert not (temp_path / "subfolder2" / "file6.g.md").exists()
        assert not (temp_path / "subfolder1" / "nested" / "file8.g.md").exists()

        # Verify that other files remain
        assert (temp_path / "file2.md").exists()
        assert (temp_path / "file3.txt").exists()
        assert (temp_path / "subfolder1" / "file5.md").exists()

        # Verify that files in hidden folders are not deleted
        assert (temp_path / ".hidden_folder" / "file7.g.md").exists()

        # Test with string path
        (temp_path / "new_file.g.md").write_text("content")
        assert (temp_path / "new_file.g.md").exists()

        result = h.md.delete_g_md_files_recursively(str(temp_path))
        assert result == "✅ Files `*.g.md` deleted"
        assert not (temp_path / "new_file.g.md").exists()


@pytest.mark.slow
def test_download_and_replace_images() -> None:
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        md_file = temp_path / "test.md"
        md_file.write_text("![Test Image](https://picsum.photos/200/300.png)")
        h.md.download_and_replace_images(md_file)
        assert "![Test Image](300.png)" not in md_file.read_text()


@pytest.mark.slow
def test_download_and_replace_images_content() -> None:
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        md_file = temp_path / "test.md"
        md_file.write_text("![Test Image](https://picsum.photos/200/300.png)")
        updated_text = h.md.download_and_replace_images_content(md_file.read_text(), temp_dir, image_folder="img")
        assert "![Test Image](300.png)" not in updated_text


def test_format_quotes_as_markdown_content() -> None:
    # Test input
    markdown_text = """They can get a big bang out of buying a blanket.

    The Catcher in the Rye
    J.D. Salinger


    I just mean that I used to think about old Spencer quite a lot

    The Catcher in the Rye
    J.D. Salinger"""

    # Expected output
    expected_output = """# The Catcher in the Rye

> They can get a big bang out of buying a blanket.
>
> -- _J.D. Salinger, The Catcher in the Rye_

---

> I just mean that I used to think about old Spencer quite a lot
>
> -- _J.D. Salinger, The Catcher in the Rye_"""

    # Call the function
    result = h.md.format_quotes_as_markdown_content(markdown_text)

    # Assert the result matches expected output
    assert result == expected_output

    # Test with multi-line quote
    multiline_text = """This is a quote
that spans multiple lines
in the text.

Book Title
Author Name


Another quote
with multiple lines
here.

Book Title
Author Name"""

    expected_multiline = """# Book Title

> This is a quote
>
> that spans multiple lines
>
> in the text.
>
> -- _Author Name, Book Title_

---

> Another quote
>
> with multiple lines
>
> here.
>
> -- _Author Name, Book Title_"""

    result_multiline = h.md.format_quotes_as_markdown_content(multiline_text)
    assert result_multiline == expected_multiline

    # Test with a temporary file using pathlib
    with TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "test_quotes.txt"

        # Write to file using pathlib
        file_path.write_text(markdown_text, encoding="utf-8")

        # Read from file using pathlib
        file_content = file_path.read_text(encoding="utf-8")

        # Process file content
        file_result = h.md.format_quotes_as_markdown_content(file_content)
        assert file_result == expected_output

    # Test with empty input
    empty_result = h.md.format_quotes_as_markdown_content("")
    assert empty_result == "# None\n\n"

    # Test with malformed input (missing author or title)
    malformed_text = """This is a quote without proper formatting.

    Only Title"""

    malformed_result = h.md.format_quotes_as_markdown_content(malformed_text)
    assert malformed_result == "# None\n\n"


def test_format_yaml() -> None:
    current_folder = h.dev.get_project_root()
    md = Path(current_folder / "tests/data/format_yaml__before.md").read_text(encoding="utf8")
    md_after = Path(current_folder / "tests/data/format_yaml__after.md").read_text(encoding="utf8")

    with TemporaryDirectory() as temp_folder:
        temp_filename = Path(temp_folder) / "temp.md"
        temp_filename.write_text(md, encoding="utf-8")
        h.md.format_yaml(temp_filename)
        md_applied = temp_filename.read_text(encoding="utf8")

    assert md_after == md_applied


def test_format_yaml_content() -> None:
    current_folder = h.dev.get_project_root()
    md = Path(current_folder / "tests/data/format_yaml__before.md").read_text(encoding="utf8")
    md_after = Path(current_folder / "tests/data/format_yaml__after.md").read_text(encoding="utf8")

    assert md_after == h.md.format_yaml_content(md)


def test_generate_author_book() -> None:
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


def test_generate_image_captions() -> None:
    current_folder = h.dev.get_project_root()
    md = Path(current_folder / "tests/data/generate_image_captions__before.md").read_text(encoding="utf8")
    md_after = Path(current_folder / "tests/data/generate_image_captions__after.md").read_text(encoding="utf8")

    with TemporaryDirectory() as temp_folder:
        temp_filename = Path(temp_folder) / "temp.md"
        temp_filename.write_text(md, encoding="utf-8")
        h.md.generate_image_captions(temp_filename)
        md_applied = temp_filename.read_text(encoding="utf8")

    assert md_after == md_applied


def test_generate_image_captions_content() -> None:
    current_folder = h.dev.get_project_root()
    md = Path(current_folder / "tests/data/generate_image_captions__before.md").read_text(encoding="utf8")
    md_after = Path(current_folder / "tests/data/generate_image_captions__after.md").read_text(encoding="utf8")
    assert md_after == h.md.generate_image_captions_content(md)


def test_append_yaml_tag() -> None:
    """Test adding YAML tag to a Markdown file."""
    md_before = """---
categories: [it, program]
tags: [VSCode, FAQ]
---

# Title

Content here.
"""

    md_after_expected = """---
categories:
- it
- program
tags:
- VSCode
- FAQ
author: Anton Sergienko
---

# Title

Content here.
"""

    with TemporaryDirectory() as temp_folder:
        temp_filename = Path(temp_folder) / "test.md"
        temp_filename.write_text(md_before, encoding="utf-8")

        result = h.md.append_yaml_tag(temp_filename, ("author", "Anton Sergienko"))
        assert "✅ File" in result

        md_after_actual = temp_filename.read_text(encoding="utf-8")
        assert md_after_expected == md_after_actual

        # Test updating existing tag
        result2 = h.md.append_yaml_tag(temp_filename, ("author", "John Doe"))
        assert "✅ File" in result2

        md_after_updated = temp_filename.read_text(encoding="utf-8")
        assert "author: John Doe" in md_after_updated

        # Test adding tag to file without YAML
        md_no_yaml = "# Title\n\nContent here.\n"
        temp_filename2 = Path(temp_folder) / "test_no_yaml.md"
        temp_filename2.write_text(md_no_yaml, encoding="utf-8")

        result3 = h.md.append_yaml_tag(temp_filename2, ("author", "Anton Sergienko"))
        assert "✅ File" in result3

        md_after_no_yaml = temp_filename2.read_text(encoding="utf-8")
        assert "author: Anton Sergienko" in md_after_no_yaml
        assert "# Title" in md_after_no_yaml

        # Test with same value (should not change)
        result4 = h.md.append_yaml_tag(temp_filename2, ("author", "Anton Sergienko"))
        assert result4 == "File is not changed."


def test_generate_short_note_toc_with_links() -> None:
    current_folder = h.dev.get_project_root()

    md_before = Path(current_folder / "tests/data/generate_short_note_toc_with_links_content__before.md").read_text(
        encoding="utf8",
    )
    md_after = Path(current_folder / "tests/data/generate_short_note_toc_with_links_content__after.md").read_text(
        encoding="utf8",
    )

    with TemporaryDirectory() as temp_folder:
        temp_filename = Path(temp_folder) / "test_document.md"
        temp_filename.write_text(md_before, encoding="utf-8")

        result = h.md.generate_short_note_toc_with_links(temp_filename)

        assert "✅ Short TOC file created:" in result
        assert str(temp_filename.with_suffix(".short.g.md")) in result

        generated_file = temp_filename.with_suffix(".short.g.md")
        assert generated_file.exists()

        generated_file_content = generated_file.read_text(encoding="utf-8")
        assert md_after == generated_file_content


def test_generate_short_note_toc_with_links_content() -> None:
    current_folder = h.dev.get_project_root()

    md_before = Path(current_folder / "tests/data/generate_short_note_toc_with_links_content__before.md").read_text(
        encoding="utf8",
    )
    md_after = Path(current_folder / "tests/data/generate_short_note_toc_with_links_content__after.md").read_text(
        encoding="utf8",
    )

    generated_content = h.md.generate_short_note_toc_with_links_content(md_before)
    assert md_after == generated_content


def test_generate_summaries() -> None:
    # Get the current year for testing
    current_year = datetime.now(UTC).year

    # Create a temporary directory for testing
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create sample year files with different formats and content

        # File with YAML frontmatter and explicit ratings
        yaml_content = """---
author: Test Author
date: 2024-06-15
---

# Books 2023

## Contents

This should be ignored.

## The Hobbit: 9

This is a great book about a hobbit.

## Lord of the Rings: 10

Epic fantasy trilogy.
"""
        (temp_path / "2023.md").write_text(yaml_content, encoding="utf-8")

        # File without YAML and with ratings in the heading line
        content_2022 = """# Books 2022

## Dune: 8

Science fiction novel.

## Foundation

This book doesn't have an explicit rating in the heading,
but has one in the line: 7

## Contents

This should be ignored.
"""
        (temp_path / "2022.md").write_text(content_2022, encoding="utf-8")

        # File with ratings in different formats
        content_2021 = """# Books 2021

## Pride and Prejudice: 9

Classic novel.

## The Great Gatsby

This has no rating.

## Moby Dick: 6

A long book about a whale.
"""
        (temp_path / "2021.md").write_text(content_2021, encoding="utf-8")

        # Run the function
        result = h.md.generate_summaries(temp_path)

        # Verify the result message
        assert "✅ File" in result
        assert "table.include.g.md is created" in result
        assert f"_{temp_path.name}.short.g.md is created" in result

        # Verify the generated files exist
        table_file = temp_path / "table.include.g.md"
        short_file = temp_path / f"_{temp_path.name}.short.g.md"
        assert table_file.exists()
        assert short_file.exists()

        # Read the generated files
        table_content = table_file.read_text(encoding="utf-8")
        short_content = short_file.read_text(encoding="utf-8")

        # Verify the table content
        assert "# Table" in table_content
        assert "| Year | Count |" in table_content

        # Verify the current year is included (without relying on the exact value)
        current_year_pattern = re.compile(rf"\| {current_year} \| \d+ \|")
        assert current_year_pattern.search(table_content) is not None

        assert "| 2023 | 2 |" in table_content  # 2 valid entries (excluding "Содержание")  # ignore: HP001
        assert "| 2022 | 2 |" in table_content  # 2 valid entries (excluding "Contents")
        assert "| 2021 | 3 |" in table_content  # 3 valid entries

        # Verify the YAML frontmatter was copied
        assert "author: Test Author" in table_content
        assert "date: 2024-06-15" in table_content
        assert "author: Test Author" in short_content
        assert "date: 2024-06-15" in short_content

        # Verify the short summary content
        assert f"# {temp_path.name}: short" in short_content

        # Verify years are in descending order
        year_positions = {}
        for year in [2023, 2022, 2021]:
            year_pos = short_content.find(f"- {year}")
            assert year_pos != -1
            year_positions[year] = year_pos

        # Check descending order
        assert year_positions[2023] < year_positions[2022] < year_positions[2021]

        # Verify book entries
        assert "  - The Hobbit: 9" in short_content
        assert "  - Lord of the Rings: 10" in short_content
        assert "  - Dune: 8" in short_content
        assert "  - Foundation" in short_content  # No rating found in the heading
        assert "  - Pride and Prejudice: 9" in short_content
        assert "  - The Great Gatsby" in short_content  # No rating
        assert "  - Moby Dick: 6" in short_content

        # Verify excluded entries don't appear
        assert "  - Содержание" not in short_content  # ignore: HP001
        assert "  - Contents" not in short_content

        # Verify the years are in descending order in the table too
        # Extract all years from the table
        table_years = re.findall(r"\| (\d{4}) \|", table_content)
        # Convert to integers
        table_years = [int(year) for year in table_years]
        # Check they're in descending order
        assert table_years == sorted(table_years, reverse=True)


def test_generate_toc_with_links() -> None:
    current_folder = h.dev.get_project_root()
    md = Path(current_folder / "tests/data/generate_toc_with_links__before.md").read_text(encoding="utf8")
    md_after = Path(current_folder / "tests/data/generate_toc_with_links__after.md").read_text(encoding="utf8")

    with TemporaryDirectory() as temp_folder:
        temp_filename = Path(temp_folder) / "temp.md"
        temp_filename.write_text(md, encoding="utf-8")
        h.md.generate_toc_with_links(temp_filename)
        md_applied = temp_filename.read_text(encoding="utf8")

    assert md_after == md_applied

    md_contents_false = """---
contents: false
lang: en
---

# Title

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [Section](#section)

</details>

## Section
Text
"""

    expected_contents_false = """---
contents: false
lang: en
---

# Title

## Section
Text
"""
    expected_contents_false = expected_contents_false.rstrip("\n") + "\n"

    assert h.md.generate_toc_with_links_content(md_contents_false) == expected_contents_false

    with TemporaryDirectory() as temp_folder:
        temp_file = Path(temp_folder) / "note.md"
        temp_file.write_text(md_contents_false, encoding="utf-8")

        h.md.generate_toc_with_links(temp_file)

        assert temp_file.read_text(encoding="utf-8") == expected_contents_false


def test_generate_toc_with_links_content() -> None:
    current_folder = h.dev.get_project_root()
    md = Path(current_folder / "tests/data/generate_toc_with_links__before.md").read_text(encoding="utf8")
    md_after = Path(current_folder / "tests/data/generate_toc_with_links__after.md").read_text(encoding="utf8")
    assert md_after == h.md.generate_toc_with_links_content(md)


def test_get_yaml_content() -> None:
    md = Path(h.dev.get_project_root() / "tests/data/get_yaml_content.md").read_text(encoding="utf8")
    yaml = h.md.get_yaml_content(md)
    correct_count_lines = 4
    assert len(yaml.splitlines()) == correct_count_lines


def test_get_set_variables_from_yaml() -> None:
    """Test collecting YAML variables from all markdown files in folder recursively."""
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test files with different YAML variables
        file1_content = """---
title: Test File 1
tags: [python, test]
categories: [it, program]
date: 2024-01-01
---

# Test Content 1
This is test content."""
        (temp_path / "file1.md").write_text(file1_content, encoding="utf-8")

        file2_content = """---
title: Test File 2
author: John Doe
tags: [markdown]
published: true
---

# Test Content 2
This is another test content."""
        (temp_path / "file2.md").write_text(file2_content, encoding="utf-8")

        # Create a subfolder with more files
        subfolder = temp_path / "subfolder"
        subfolder.mkdir()

        file3_content = """---
title: Test File 3
date: 2024-01-02
lang: en
---

# Test Content 3
This is content in subfolder."""
        (subfolder / "file3.md").write_text(file3_content, encoding="utf-8")

        # Create a file without YAML
        file4_content = """# Test Content 4
This file has no YAML."""
        (temp_path / "file4.md").write_text(file4_content, encoding="utf-8")

        # Create a hidden folder (should be ignored)
        hidden_folder = temp_path / ".hidden"
        hidden_folder.mkdir()
        hidden_file_content = """---
title: Hidden File
secret: true
---

# Hidden Content"""
        (hidden_folder / "hidden.md").write_text(hidden_file_content, encoding="utf-8")

        # Call the function
        variables = h.md.get_set_variables_from_yaml(temp_path)

        # Check that all unique variables are collected
        expected_variables = ["author", "categories", "date", "lang", "published", "tags", "title"]
        assert variables == expected_variables

        # Verify that variables from hidden folder are not included
        assert "secret" not in variables

        # Test with empty folder
        with TemporaryDirectory() as empty_dir:
            empty_variables = h.md.get_set_variables_from_yaml(empty_dir)
            assert empty_variables == []

        # Test with folder containing only files without YAML
        with TemporaryDirectory() as no_yaml_dir:
            no_yaml_path = Path(no_yaml_dir)
            (no_yaml_path / "file.md").write_text("# No YAML", encoding="utf-8")
            no_yaml_variables = h.md.get_set_variables_from_yaml(no_yaml_path)
            assert no_yaml_variables == []


def test_identify_code_blocks() -> None:
    md = Path(h.dev.get_project_root() / "tests/data/generate_image_captions__before.md").read_text(encoding="utf8")
    _, content = h.md.split_yaml_content(md)
    count_lines_content = 0
    count_lines_code = 0
    for _, state in h.md.identify_code_blocks(content.splitlines()):
        if state:
            count_lines_code += 1
        else:
            count_lines_content += 1
    correct_count_lines_code = 9
    assert count_lines_code == correct_count_lines_code
    correct_count_lines_content = 22
    assert count_lines_content == correct_count_lines_content


def test_identify_code_blocks_line() -> None:
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


def test_increase_heading_level_content() -> None:
    md_text = """# Heading
This is some text.

## Subheading
More text here."""

    expected = """## Heading
This is some text.

### Subheading
More text here."""
    assert h.md.increase_heading_level_content(md_text) == expected


def test_decrease_heading_level_content() -> None:
    md_text = """## Heading
This is some text.

### Subheading
More text here.

# Single heading
Should remain unchanged."""

    expected = """# Heading
This is some text.

## Subheading
More text here.

# Single heading
Should remain unchanged."""

    assert h.md.decrease_heading_level_content(md_text) == expected


def test_remove_toc_content() -> None:
    current_folder = h.dev.get_project_root()
    md = Path(current_folder / "tests/data/generate_toc_with_links__after.md").read_text(encoding="utf8")
    md_after = Path(current_folder / "tests/data/generate_toc_with_links__before.md").read_text(encoding="utf8")
    assert md_after == h.md.remove_toc_content(md)


def test_remove_yaml_and_code_content() -> None:
    md = Path(h.dev.get_project_root() / "tests/data/remove_yaml_and_code_content.md").read_text(encoding="utf8")
    md_clean = h.md.remove_yaml_and_code_content(md)
    correct_count_lines = 26
    assert len(md_clean.splitlines()) == correct_count_lines


def test_remove_yaml_content() -> None:
    md = Path(h.dev.get_project_root() / "tests/data/get_yaml_content.md").read_text(encoding="utf8")
    md_clean = h.md.remove_yaml_content(md)
    correct_count_lines = 1
    assert len(md_clean.splitlines()) == correct_count_lines


def test_replace_section() -> None:
    with TemporaryDirectory() as temp_dir:
        # Create a test file with some content
        test_file_path = Path(temp_dir) / "testfile.md"
        original_content = """# Header

Some content here

## 📋 List of commands

- command1

###  Subsection

- command2

## Footer

More content here
"""
        with Path.open(test_file_path, "w", encoding="utf-8") as file:
            file.write(original_content)

        # New content to replace the section
        new_content = "New list of commands:\n\n- new command1\n- new command2"

        # Call the function to replace the section
        h.md.replace_section(test_file_path, new_content)

        # Read the modified file content
        with Path.open(test_file_path, encoding="utf-8") as file:
            updated_content = file.read()

        # Expected content after replacement
        expected_content = """# Header

Some content here

## 📋 List of commands

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

## 📋 List of commands

- command1

###  Subsection

- command2

### Footer

More content here

#### Sub

Text.
"""
        with Path.open(test_file_path, "w", encoding="utf-8") as file:
            file.write(original_content)

        # New content to replace the section
        new_content = "New list of commands:\n\n- new command1\n- new command2"

        # Call the function to replace the section
        h.md.replace_section(test_file_path, new_content, "### Footer")

        # Read the modified file content
        with Path.open(test_file_path, encoding="utf-8") as file:
            updated_content = file.read()

        # Expected content after replacement
        expected_content = """# Header

Some content here

## 📋 List of commands

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


def test_replace_section_content() -> None:
    original_content = """# Header

Some content here

## 📋 List of commands

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

## 📋 List of commands

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

## 📋 List of commands

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

## 📋 List of commands

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


def test_sort_sections() -> None:
    current_folder = h.dev.get_project_root()

    # Test default behavior (always sort)
    md = Path(current_folder / "tests/data/sort_sections__before.md").read_text(encoding="utf8")
    md_after = Path(current_folder / "tests/data/sort_sections__after.md").read_text(encoding="utf8")

    with TemporaryDirectory() as temp_folder:
        temp_filename = Path(temp_folder) / "temp.md"
        temp_filename.write_text(md, encoding="utf-8")
        h.md.sort_sections(temp_filename)
        md_applied = temp_filename.read_text(encoding="utf8")

    assert md_after == md_applied

    # Test with is_sort_section_from_yaml=True and sort-section: true (should sort)
    md_yaml_true = Path(current_folder / "tests/data/sort_sections_yaml_true__before.md").read_text(encoding="utf8")
    md_yaml_after = Path(current_folder / "tests/data/sort_sections_yaml_true__after.md").read_text(encoding="utf8")

    with TemporaryDirectory() as temp_folder:
        temp_filename = Path(temp_folder) / "temp_yaml_true.md"
        temp_filename.write_text(md_yaml_true, encoding="utf-8")
        h.md.sort_sections(temp_filename, is_sort_section_from_yaml=True)
        md_applied_yaml_true = temp_filename.read_text(encoding="utf8")

    assert md_yaml_after == md_applied_yaml_true

    # Test with is_sort_section_from_yaml=True and sort-section: false (should NOT sort)
    md_yaml_false = Path(current_folder / "tests/data/sort_sections_yaml_false__before.md").read_text(encoding="utf8")

    with TemporaryDirectory() as temp_folder:
        temp_filename = Path(temp_folder) / "temp_yaml_false.md"
        temp_filename.write_text(md_yaml_false, encoding="utf-8")
        h.md.sort_sections(temp_filename, is_sort_section_from_yaml=True)
        md_applied_yaml_false = temp_filename.read_text(encoding="utf8")

    # Should remain unchanged when sort-section: false
    assert md_yaml_false == md_applied_yaml_false

    # Test with is_sort_section_from_yaml=True and no sort-section parameter (should NOT sort)
    md_yaml_none = Path(current_folder / "tests/data/sort_sections_yaml_none__before.md").read_text(encoding="utf8")

    with TemporaryDirectory() as temp_folder:
        temp_filename = Path(temp_folder) / "temp_yaml_none.md"
        temp_filename.write_text(md_yaml_none, encoding="utf-8")
        h.md.sort_sections(temp_filename, is_sort_section_from_yaml=True)
        md_applied_yaml_none = temp_filename.read_text(encoding="utf8")

    # Should remain unchanged when sort-section parameter is missing
    assert md_yaml_none == md_applied_yaml_none


def test_sort_sections_content() -> None:
    current_folder = h.dev.get_project_root()

    # Test default behavior (always sort)
    md = Path(current_folder / "tests/data/sort_sections__before.md").read_text(encoding="utf8")
    md_after = Path(current_folder / "tests/data/sort_sections__after.md").read_text(encoding="utf8")
    md_applied = h.md.sort_sections_content(md)
    assert md_after == md_applied

    # Test with is_sort_section_from_yaml=True and sort-section: true (should sort)
    md_yaml_true = Path(current_folder / "tests/data/sort_sections_yaml_true__before.md").read_text(encoding="utf8")
    md_yaml_after = Path(current_folder / "tests/data/sort_sections_yaml_true__after.md").read_text(encoding="utf8")
    md_applied_yaml_true = h.md.sort_sections_content(md_yaml_true, is_sort_section_from_yaml=True)
    assert md_yaml_after == md_applied_yaml_true

    # Test with is_sort_section_from_yaml=True and sort-section: false (should NOT sort)
    md_yaml_false = Path(current_folder / "tests/data/sort_sections_yaml_false__before.md").read_text(encoding="utf8")
    md_applied_yaml_false = h.md.sort_sections_content(md_yaml_false, is_sort_section_from_yaml=True)
    # Should remain unchanged when sort-section: false
    assert md_yaml_false == md_applied_yaml_false

    # Test with is_sort_section_from_yaml=True and no sort-section parameter (should NOT sort)
    md_yaml_none = Path(current_folder / "tests/data/sort_sections_yaml_none__before.md").read_text(encoding="utf8")
    md_applied_yaml_none = h.md.sort_sections_content(md_yaml_none, is_sort_section_from_yaml=True)
    # Should remain unchanged when sort-section parameter is missing
    assert md_yaml_none == md_applied_yaml_none


def test_split_toc_content_basic() -> None:
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


def test_split_yaml_content() -> None:
    md = Path(h.dev.get_project_root() / "tests/data/get_yaml_content.md").read_text(encoding="utf8")
    yaml, content = h.md.split_yaml_content(md)
    correct_count_lines = 5
    assert len(yaml.splitlines()) + len(content.splitlines()) == correct_count_lines


def test_generate_id() -> None:
    """Test the generate_id function with various inputs and edge cases."""
    existing_ids = set()

    # Test basic functionality
    assert h.md.generate_id("My Great Heading", existing_ids) == "my-great-heading"
    assert "my-great-heading" in existing_ids

    # Test uniqueness - same text should get suffix
    assert h.md.generate_id("My Great Heading", existing_ids) == "my-great-heading-1"
    assert "my-great-heading-1" in existing_ids

    # Test another duplicate
    assert h.md.generate_id("My Great Heading", existing_ids) == "my-great-heading-2"
    assert "my-great-heading-2" in existing_ids

    # Test different text
    assert h.md.generate_id("Another Heading", existing_ids) == "another-heading"
    assert "another-heading" in existing_ids

    # Test underscores and hyphens are preserved
    assert h.md.generate_id("test_with-dashes_and_underscores", existing_ids) == "test_with-dashes_and_underscores"

    # Test numbers are preserved
    assert h.md.generate_id("Heading 123 with numbers", existing_ids) == "heading-123-with-numbers"

    # Test multiple spaces become single hyphens
    assert h.md.generate_id("Multiple    spaces   here", existing_ids) == "multiple----spaces---here"

    # Test empty string and edge cases
    assert h.md.generate_id("", existing_ids) == ""
    assert h.md.generate_id("   ", existing_ids) == "---"

    # Test unicode characters
    assert h.md.generate_id("Заголовок на русском", existing_ids) == "заголовок-на-русском"

    # Test emoji handling (if remove_markdown_formatting handles it)
    result = h.md.generate_id("Heading with 😀 emoji", existing_ids)
    assert "heading-with" in result

    # Test markdown formatting removal
    result = h.md.generate_id("**Bold** and *italic* text", existing_ids)
    assert result == "bold-and-italic-text"

    # Test leading/trailing spaces
    assert h.md.generate_id("  spaced heading  ", existing_ids) == "--spaced-heading--"

    # Test case sensitivity
    new_ids = set()
    assert h.md.generate_id("UPPERCASE", new_ids) == "uppercase"
    assert h.md.generate_id("lowercase", new_ids) == "lowercase"
    assert h.md.generate_id("MixedCase", new_ids) == "mixedcase"


def test_remove_markdown_formatting_for_headings() -> None:
    """Test remove_markdown_formatting_for_headings function with various markdown formats."""
    # Test bold formatting removal
    assert h.md.remove_markdown_formatting_for_headings("**Bold text**") == "Bold text"
    assert h.md.remove_markdown_formatting_for_headings("**Multiple** **bold** **words**") == "Multiple bold words"

    # Test italic formatting removal
    assert h.md.remove_markdown_formatting_for_headings("*Italic text*") == "Italic text"
    assert h.md.remove_markdown_formatting_for_headings("*Multiple* *italic* *words*") == "Multiple italic words"

    # Test strikethrough formatting removal
    assert h.md.remove_markdown_formatting_for_headings("~~Strikethrough text~~") == "Strikethrough text"
    assert (
        h.md.remove_markdown_formatting_for_headings("~~Multiple~~ ~~strikethrough~~ ~~words~~")
        == "Multiple strikethrough words"
    )

    # Test autolinks removal
    assert h.md.remove_markdown_formatting_for_headings("<https://example.com>") == ""
    assert h.md.remove_markdown_formatting_for_headings("<http://example.com>") == ""
    assert (
        h.md.remove_markdown_formatting_for_headings("Visit <https://example.com> for more info")
        == "Visit  for more info"
    )

    # Test combined formatting
    combined_text = "**Bold** and *italic* with ~~strikethrough~~ and <https://example.com>"
    expected = "Bold and italic with strikethrough and "
    assert h.md.remove_markdown_formatting_for_headings(combined_text) == expected

    # Test empty string
    assert h.md.remove_markdown_formatting_for_headings("") == ""

    # Test plain text (no formatting)
    plain_text = "Just plain text with no formatting"
    assert h.md.remove_markdown_formatting_for_headings(plain_text) == plain_text

    # Test nested formatting (current function behavior - doesn't handle nested properly)
    assert h.md.remove_markdown_formatting_for_headings("**Bold with *italic* inside**") == "*Bold with italic inside*"

    # Test text with special characters
    special_text = "Text with symbols: @#$%^&*()_+-=[]{}|;':\",./<>?"
    assert h.md.remove_markdown_formatting_for_headings(special_text) == special_text

    # Test multiple autolinks
    multiple_links = "Check <https://site1.com> and <http://site2.com> for details"
    assert h.md.remove_markdown_formatting_for_headings(multiple_links) == "Check  and  for details"

    # Test separate bold and italic (not nested)
    separate_formatting = "**Bold text** and *italic text* separately"
    assert h.md.remove_markdown_formatting_for_headings(separate_formatting) == "Bold text and italic text separately"
