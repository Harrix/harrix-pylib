"""Tests for the functions in the file module of harrix_pylib."""

import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

import harrix_pylib as h


def test_all_to_parent_folder() -> None:
    with TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        folder1 = base_path / "folder1"
        folder2 = base_path / "folder2"
        folder1.mkdir()
        folder2.mkdir()

        (folder1 / "image.jpg").touch()
        (folder1 / "sub1").mkdir()
        (folder1 / "sub1" / "file1.txt").touch()
        (folder1 / "sub2").mkdir()
        (folder1 / "sub2" / "file3.txt").touch()

        sub3 = folder2 / "sub3"
        sub3.mkdir()
        (sub3 / "file6.txt").touch()
        sub4 = sub3 / "sub4"
        sub4.mkdir()
        (sub4 / "file5.txt").touch()

        # Now perform the test
        result = h.file.all_to_parent_folder(str(base_path))
        assert (base_path / "folder1" / "file1.txt").exists()
        assert (base_path / "folder1" / "file3.txt").exists()
        assert (base_path / "folder2" / "file5.txt").exists()
        assert (base_path / "folder2" / "file6.txt").exists()
        assert not (base_path / "folder1" / "sub1").exists()
        assert not (base_path / "folder1" / "sub2").exists()
        assert not (base_path / "folder2" / "sub3" / "sub4").exists()
        assert "folder1" in result
        assert "folder2" in result


def test_apply_func() -> None:
    def test_func(filename: Path | str) -> None:
        content = Path(filename).read_text(encoding="utf8")
        content = content.upper()
        Path(filename).write_text(content, encoding="utf8")

    with TemporaryDirectory() as temp_folder:
        file1 = Path(temp_folder) / "file1.txt"
        file2 = Path(temp_folder) / "file2.txt"
        Path(file1).write_text("text", encoding="utf8")
        Path(file2).write_text("other", encoding="utf8")
        h.file.apply_func(temp_folder, ".txt", test_func)
        result = file1.read_text(encoding="utf8") + " " + file2.read_text(encoding="utf8")

    assert result == "TEXT OTHER"


def test_check_featured_image() -> None:
    folder = h.dev.get_project_root() / "tests/data/check_featured_image/folder_correct"
    assert h.file.check_featured_image(folder)[0]
    folder = h.dev.get_project_root() / "tests/data/check_featured_image/folder_wrong"
    assert not h.file.check_featured_image(folder)[0]


def test_check_func() -> None:
    # Define a test checking function
    def test_checker(file_path: Path | str) -> list[str]:
        path = Path(file_path)
        with path.open("r") as f:
            content = f.read()
        errors = []
        if "error" in content.lower():
            errors.append(f"Error found in {path.name}")
        min_length_content = 5
        if len(content) < min_length_content:
            errors.append(f"Content too short in {path.name}")
        return errors

    # Create a temporary directory structure for testing
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test files with different extensions
        files = {
            "file1.txt": "This is a normal file",
            "file2.txt": "Error in this file",
            "file3.txt": "OK",
            "file4.md": "This is not a txt file",
            ".hidden.txt": "This is hidden",
            "subdir/nested.txt": "Nested error file",
            "subdir/.hidden_nested.txt": "Hidden nested",
            "subdir/normal_nested.txt": "Normal nested file",
            ".hidden_dir/hidden_file.txt": "File in hidden dir",
        }

        # Create the files in the temporary directory
        for file_path, content in files.items():
            full_path = temp_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with Path.open(full_path, "w") as f:
                f.write(content)

        # Test the check_func with .txt extension
        results = h.file.check_func(temp_path, ".txt", test_checker)

        # Expected results based on our test files and checker function
        expected_errors = [
            "Error found in file2.txt",
            "Content too short in file3.txt",
            "Error found in nested.txt",
        ]

        # Sort both lists to ensure order doesn't affect comparison
        results.sort()
        expected_errors.sort()

        # Assertions
        count_errors = 3
        assert len(results) == count_errors, f"Expected 3 errors, got {len(results)}: {results}"
        assert results == expected_errors, f"Results don't match expected: {results} vs {expected_errors}"

        # Test with a different extension
        md_results = h.file.check_func(temp_path, ".md", test_checker)
        assert len(md_results) == 0, f"Expected 0 errors for .md files, got {len(md_results)}: {md_results}"

        # Test with a non-existent extension
        no_results = h.file.check_func(temp_path, ".nonexistent", test_checker)
        assert len(no_results) == 0, "Expected 0 errors for non-existent extension"


def test_clear_directory() -> None:
    folder = h.dev.get_project_root() / "tests/data/temp"
    folder.mkdir(parents=True, exist_ok=True)
    Path(folder / "temp.txt").write_text("Hello, world!", encoding="utf8")
    h.file.clear_directory(folder)
    assert len(next(os.walk(folder))[2]) == 0
    shutil.rmtree(folder)


def test_find_max_folder_number() -> None:
    folder = h.dev.get_project_root() / "tests/data/check_featured_image/folder_correct"
    correct_max_folder_number = 2
    assert h.file.find_max_folder_number(str(folder), "folder") == correct_max_folder_number


def test_open_file_or_folder() -> None:
    with pytest.raises(FileNotFoundError):
        h.file.open_file_or_folder("this_path_does_not_exist")


def test_rename_largest_images_to_featured() -> None:
    # Test with a temporary directory structure
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create subdirectories
        subdir1 = temp_path / "subdir1"  # Multiple images of different sizes
        subdir2 = temp_path / "subdir2"  # Only one image
        subdir3 = temp_path / "subdir3"  # Empty directory
        subdir4 = temp_path / "subdir4"  # Directory with existing featured image

        for subdir in [subdir1, subdir2, subdir3, subdir4]:
            subdir.mkdir()

        # Create test image files with different sizes
        # Subdir1 - small.jpg (1KB), medium.png (2KB), large.jpg (3KB)
        with Path.open(subdir1 / "small.jpg", "wb") as f:
            f.write(b"0" * 1024)
        with Path.open(subdir1 / "medium.png", "wb") as f:
            f.write(b"0" * 2048)
        with Path.open(subdir1 / "large.jpg", "wb") as f:
            f.write(b"0" * 3072)

        # Subdir2 - only one image
        with Path.open(subdir2 / "only_image.png", "wb") as f:
            f.write(b"0" * 1024)

        # Subdir4 - with existing featured-image.jpg
        with Path.open(subdir4 / "image1.jpg", "wb") as f:
            f.write(b"0" * 1024)
        with Path.open(subdir4 / "featured-image.jpg", "wb") as f:
            f.write(b"0" * 512)

        # Create a test file to test file path handling
        test_file = temp_path / "test_file.txt"
        with Path.open(test_file, "w") as f:
            f.write("test")

        # Test 1: Run the function with the temp directory
        result = h.file.rename_largest_images_to_featured(temp_path)

        # Check if the function output contains expected messages
        assert "Processing directory" in result
        assert "Total files renamed:" in result
        assert "No image files found in" in result  # For empty directory
        assert "Warning: " in result  # For the directory with existing featured image

        # Check if the largest files were correctly renamed
        assert (subdir1 / "featured-image.jpg").exists()
        assert not (subdir1 / "large.jpg").exists()  # Original should be gone
        assert (subdir1 / "small.jpg").exists()  # Others should remain
        assert (subdir1 / "medium.png").exists()

        assert (subdir2 / "featured-image.png").exists()
        assert not (subdir2 / "only_image.png").exists()

        # No files should be renamed in subdir3 (empty)
        assert len(list(subdir3.glob("*"))) == 0

        # In subdir4, the existing featured-image.jpg should remain
        assert (subdir4 / "featured-image.jpg").exists()
        assert (subdir4 / "image1.jpg").exists()  # Should not be renamed

        # Test 2: Test with string path instead of Path object
        # Create a new subdirectory with an image for this test
        string_test_dir = temp_path / "string_test"
        string_test_dir.mkdir()
        with Path.open(string_test_dir / "image.jpg", "wb") as f:
            f.write(b"0" * 1024)

        # Use string path
        string_result = h.file.rename_largest_images_to_featured(str(temp_path))

        # Check if renaming worked
        assert "Renaming 'image.jpg' to 'featured-image.jpg'" in string_result
        assert (string_test_dir / "featured-image.jpg").exists()

        # Test 3: Test with invalid paths
        # Test with non-existent directory
        with pytest.raises(ValueError, match="is not a valid directory"):
            h.file.rename_largest_images_to_featured("/path/that/does/not/exist")

        # Test with a file path instead of directory
        with pytest.raises(ValueError, match="is not a valid directory"):
            h.file.rename_largest_images_to_featured(test_file)


def test_tree_view_folder() -> None:
    current_folder = h.dev.get_project_root()
    tree_check = (current_folder / "tests/data/tree_view_folder__01.txt").read_text(encoding="utf8")
    folder_path = current_folder / "tests/data/tree_view_folder"
    assert h.file.tree_view_folder(folder_path) == tree_check
    tree_check = (current_folder / "tests/data/tree_view_folder__02.txt").read_text(encoding="utf8")
    assert h.file.tree_view_folder(folder_path, is_ignore_hidden_folders=True) == tree_check


def test_rename_fb2_file() -> None:
    """Test the h.file.rename_fb2_file function with various scenarios."""
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Test 1: FB2 file with complete metadata (author, title, year)
        fb2_content_complete = """<?xml version="1.0" encoding="utf-8"?>
<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0">
<description>
<title-info>
<author>
<first-name>Лев</first-name>
<last-name>Толстой</last-name>
</author>
<book-title>Война и мир</book-title>
<date>1869</date>
</title-info>
</description>
<body>
<section>
<title><p>Глава 1</p></title>
<p>Текст книги...</p>
</section>
</body>
</FictionBook>"""

        complete_file = temp_path / "random_name_123.fb2"
        complete_file.write_text(fb2_content_complete, encoding="utf-8")

        result = h.file.rename_fb2_file(complete_file)
        assert "✅ File renamed:" in result
        assert "Толстой Лев - Война и мир - 1869.fb2" in result
        assert (temp_path / "Толстой Лев - Война и мир - 1869.fb2").exists()
        assert not complete_file.exists()

        # Test 2: FB2 file with metadata but no year
        fb2_content_no_year = """<?xml version="1.0" encoding="utf-8"?>
<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0">
<description>
<title-info>
<author>
<first-name>Александр</first-name>
<last-name>Пушкин</last-name>
</author>
<book-title>Евгений Онегин</book-title>
</title-info>
</description>
<body>
<section>
<p>Текст книги...</p>
</section>
</body>
</FictionBook>"""

        no_year_file = temp_path / "another_random.fb2"
        no_year_file.write_text(fb2_content_no_year, encoding="utf-8")

        result = h.file.rename_fb2_file(no_year_file)
        assert "✅ File renamed:" in result
        assert "Пушкин Александр - Евгений Онегин.fb2" in result
        assert (temp_path / "Пушкин Александр - Евгений Онегин.fb2").exists()

        # Test 3: FB2 file with reversed author name order (last-name first)
        fb2_content_reversed = """<?xml version="1.0" encoding="utf-8"?>
<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0">
<description>
<title-info>
<author>
<last-name>Достоевский</last-name>
<first-name>Федор</first-name>
</author>
<book-title>Преступление и наказание</book-title>
<year>1866</year>
</title-info>
</description>
<body>
<section>
<p>Текст книги...</p>
</section>
</body>
</FictionBook>"""

        reversed_file = temp_path / "xyz123.fb2"
        reversed_file.write_text(fb2_content_reversed, encoding="utf-8")

        result = h.file.rename_fb2_file(reversed_file)
        assert "✅ File renamed:" in result
        # The function should still format as "LastName FirstName"
        assert "Достоевский Федор - Преступление и наказание - 1866.fb2" in result

        # Test 4: FB2 file with invalid characters in metadata
        fb2_content_invalid_chars = """<?xml version="1.0" encoding="utf-8"?>
<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0">
<description>
<title-info>
<author>
<first-name>Иван</first-name>
<last-name>Тургенев</last-name>
</author>
<book-title>Отцы и дети: роман</book-title>
<year>1862</year>
</title-info>
</description>
<body>
<section>
<p>Текст книги...</p>
</section>
</body>
</FictionBook>"""

        invalid_chars_file = temp_path / "testfile.fb2"
        invalid_chars_file.write_text(fb2_content_invalid_chars, encoding="utf-8")

        result = h.file.rename_fb2_file(invalid_chars_file)
        assert "✅ File renamed:" in result
        assert "Тургенев Иван - Отцы и дети роман - 1862.fb2" in result

        # Test 5: FB2 file with Windows-1251 encoding
        fb2_content_cp1251 = """<?xml version="1.0" encoding="windows-1251"?>
<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0">
<description>
<title-info>
<author>
<first-name>Антон</first-name>
<last-name>Чехов</last-name>
</author>
<book-title>Вишневый сад</book-title>
</title-info>
</description>
<body>
<section>
<p>Текст пьесы...</p>
</section>
</body>
</FictionBook>"""

        cp1251_file = temp_path / "cp1251_test.fb2"
        cp1251_file.write_bytes(fb2_content_cp1251.encode("windows-1251"))

        result = h.file.rename_fb2_file(cp1251_file)
        assert "✅ File renamed:" in result
        assert "Чехов Антон - Вишневый сад.fb2" in result

        # Test 6: FB2 file with author in single field (testing format_author_name function)
        fb2_content_single_author = """<?xml version="1.0" encoding="utf-8"?>
<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0">
<description>
<title-info>
<author>Михаил Лермонтов</author>
<book-title>Герой нашего времени</book-title>
<year>1840</year>
</title-info>
</description>
<body>
<section>
<p>Текст книги...</p>
</section>
</body>
</FictionBook>"""

        single_author_file = temp_path / "single_author.fb2"
        single_author_file.write_text(fb2_content_single_author, encoding="utf-8")

        result = h.file.rename_fb2_file(single_author_file)
        assert "✅ File renamed:" in result
        assert "Лермонтов Михаил - Герой нашего времени - 1840.fb2" in result

        # Test 7: FB2 file with author having middle name
        fb2_content_middle_name = """<?xml version="1.0" encoding="utf-8"?>
<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0">
<description>
<title-info>
<author>
<first-name>Александр Сергеевич</first-name>
<last-name>Пушкин</last-name>
</author>
<book-title>Капитанская дочка</book-title>
<year>1836</year>
</title-info>
</description>
<body>
<section>
<p>Текст книги...</p>
</section>
</body>
</FictionBook>"""

        middle_name_file = temp_path / "middle_name.fb2"
        middle_name_file.write_text(fb2_content_middle_name, encoding="utf-8")

        result = h.file.rename_fb2_file(middle_name_file)
        assert "✅ File renamed:" in result
        assert "Пушкин Александр Сергеевич - Капитанская дочка - 1836.fb2" in result

        # Test 8: File with transliterated Russian name (mock transliteration)
        transliterated_file = temp_path / "voyna_i_mir.fb2"
        # Create a file with no valid metadata
        invalid_content = """<?xml version="1.0" encoding="utf-8"?>
<FictionBook>
<description>
<title-info>
</title-info>
</description>
<body>
<p>No metadata</p>
</body>
</FictionBook>"""
        transliterated_file.write_text(invalid_content, encoding="utf-8")

        result = h.file.rename_fb2_file(transliterated_file)
        # The result depends on transliteration library behavior
        # It should either rename or leave unchanged
        assert "✅ File renamed:" in result or "📝 File" in result

        # Test 9: Non-FB2 file
        txt_file = temp_path / "test.txt"
        txt_file.write_text("This is not an FB2 file")

        result = h.file.rename_fb2_file(txt_file)
        assert "❌ File" in result
        assert "is not an FB2 file" in result

        # Test 10: Non-existent file
        non_existent = temp_path / "does_not_exist.fb2"
        result = h.file.rename_fb2_file(non_existent)
        assert "❌ File" in result
        assert "does not exist" in result

        # Test 11: File with no extractable metadata and no transliteration improvement
        no_metadata_file = temp_path / "no_metadata_123.fb2"
        minimal_content = """<?xml version="1.0" encoding="utf-8"?>
<FictionBook>
<description>
</description>
<body>
<p>Minimal content</p>
</body>
</FictionBook>"""
        no_metadata_file.write_text(minimal_content, encoding="utf-8")

        result = h.file.rename_fb2_file(no_metadata_file)
        assert "📝 File" in result
        assert "left unchanged" in result

        # Test 12: File name collision handling
        collision_file1 = temp_path / "collision_test.fb2"
        collision_file1.write_text(fb2_content_complete, encoding="utf-8")

        # Create a file that would have the same target name
        target_name = temp_path / "Толстой Лев - Война и мир - 1869.fb2"
        if not target_name.exists():
            target_name.write_text("existing file", encoding="utf-8")

        collision_file2 = temp_path / "collision_test2.fb2"
        collision_file2.write_text(fb2_content_complete, encoding="utf-8")

        result = h.file.rename_fb2_file(collision_file2)
        assert "✅ File renamed:" in result
        # Should create a file with (1) suffix or similar
        assert any(f.name.startswith("Толстой Лев - Война и мир - 1869") for f in temp_path.glob("*.fb2"))

        # Test 13: Test with Path object input
        path_test_file = temp_path / "path_test.fb2"
        path_test_file.write_text(fb2_content_no_year, encoding="utf-8")

        result = h.file.rename_fb2_file(path_test_file)  # Path object
        assert "✅ File renamed:" in result

        # Test 14: Test with string input
        string_test_file = temp_path / "string_test.fb2"
        string_test_file.write_text(fb2_content_no_year, encoding="utf-8")

        result = h.file.rename_fb2_file(str(string_test_file))  # String path
        assert "✅ File renamed:" in result

        # Test 15: Test with only one name part
        fb2_content_single_name = """<?xml version="1.0" encoding="utf-8"?>
<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0">
<description>
<title-info>
<author>Гомер</author>
<book-title>Илиада</book-title>
</title-info>
</description>
<body>
<section>
<p>Текст книги...</p>
</section>
</body>
</FictionBook>"""

        single_name_file = temp_path / "single_name.fb2"
        single_name_file.write_text(fb2_content_single_name, encoding="utf-8")

        result = h.file.rename_fb2_file(single_name_file)
        assert "✅ File renamed:" in result
        assert "Гомер - Илиада.fb2" in result
