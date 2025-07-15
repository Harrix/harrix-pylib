"""Tests for the functions in the file module of harrix_pylib."""

import os
import shutil
import zipfile
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


def test_list_files_simple() -> None:
    current_folder = h.dev.get_project_root()
    files_check = (current_folder / "tests/data/list_files_simple__01.txt").read_text(encoding="utf8")
    folder_path = current_folder / "tests/data/tree_view_folder"
    assert h.file.list_files_simple(folder_path) == files_check
    files_check = (current_folder / "tests/data/list_files_simple__02.txt").read_text(encoding="utf8")
    assert h.file.list_files_simple(folder_path, is_ignore_hidden_folders=True) == files_check

    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test structure
        (temp_path / "file1.txt").touch()
        (temp_path / "file2.md").touch()
        (temp_path / "subfolder").mkdir()
        (temp_path / "subfolder" / "nested_file.txt").touch()
        (temp_path / "subfolder" / "another_folder").mkdir()
        (temp_path / "subfolder" / "another_folder" / "deep_file.py").touch()

        # Test with is_only_files=True - should only return files from current directory
        result = h.file.list_files_simple(temp_path, is_only_files=True)
        expected_files = ["file1.txt", "file2.md"]
        result_files = result.split("\n") if result else []

        assert len(result_files) == 2
        assert "file1.txt" in result_files
        assert "file2.md" in result_files
        assert "nested_file.txt" not in result_files
        assert "deep_file.py" not in result_files

        # Test with is_only_files=False (default) - should return all files recursively
        result_all = h.file.list_files_simple(temp_path, is_only_files=False)
        expected_all_files = [
            "file1.txt",
            "file2.md",
            "subfolder/nested_file.txt",
            "subfolder/another_folder/deep_file.py",
        ]
        result_all_files = result_all.split("\n") if result_all else []

        assert len(result_all_files) == 4
        for expected_file in expected_all_files:
            assert expected_file in result_all_files


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


def test_rename_file_spaces_to_hyphens() -> None:
    """Test the h.file.rename_file_spaces_to_hyphens function with various scenarios."""
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Test 1: FB2 file with spaces in name
        file_with_spaces = temp_path / "my book title.fb2"
        file_with_spaces.write_text("Test content", encoding="utf-8")

        result = h.file.rename_file_spaces_to_hyphens(file_with_spaces)
        assert "✅ File renamed:" in result
        assert "my-book-title.fb2" in result
        assert (temp_path / "my-book-title.fb2").exists()
        assert not file_with_spaces.exists()

        # Test 2: PDF file with multiple spaces
        file_multiple_spaces = temp_path / "author name - book title.pdf"
        file_multiple_spaces.write_text("Test content", encoding="utf-8")

        result = h.file.rename_file_spaces_to_hyphens(file_multiple_spaces)
        assert "✅ File renamed:" in result
        assert "author-name---book-title.pdf" in result
        assert (temp_path / "author-name---book-title.pdf").exists()

        # Test 3: TXT file with no spaces (should remain unchanged)
        file_no_spaces = temp_path / "filename.txt"
        file_no_spaces.write_text("Test content", encoding="utf-8")

        result = h.file.rename_file_spaces_to_hyphens(file_no_spaces)
        assert "📝 File" in result
        assert "left unchanged" in result
        assert "no spaces found" in result
        assert file_no_spaces.exists()

        # Test 4: Non-existent file
        non_existent = temp_path / "non_existent.txt"
        result = h.file.rename_file_spaces_to_hyphens(non_existent)
        assert "❌ File" in result
        assert "does not exist" in result


def test_rename_epub_file() -> None:
    """Test rename_epub_file function with various scenarios."""

    def create_epub_file(file_path: Path, author: str = "", title: str = "", year: str = "") -> None:
        """Create a minimal EPUB file with specified metadata."""
        with zipfile.ZipFile(file_path, "w") as epub_zip:
            # Create mimetype file
            epub_zip.writestr("mimetype", "application/epub+zip")

            # Create container.xml
            container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>"""
            epub_zip.writestr("META-INF/container.xml", container_xml)

            # Create OPF file with metadata
            opf_content = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">"""

            if author:
                opf_content += f"<dc:creator>{author}</dc:creator>"
            if title:
                opf_content += f"<dc:title>{title}</dc:title>"
            if year:
                opf_content += f"<dc:date>{year}</dc:date>"

            opf_content += """
    </metadata>
    <manifest>
        <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    </manifest>
    <spine toc="ncx">
    </spine>
</package>"""

            epub_zip.writestr("OEBPS/content.opf", opf_content)

            # Create minimal toc.ncx
            toc_ncx = """<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
    <head>
        <meta name="dtb:uid" content="test"/>
    </head>
    <docTitle>
        <text>Test Book</text>
    </docTitle>
    <navMap>
    </navMap>
</ncx>"""
            epub_zip.writestr("OEBPS/toc.ncx", toc_ncx)

    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Test 1: Non-existent file
        non_existent = temp_path / "non_existent.epub"
        result = h.file.rename_epub_file(non_existent)
        assert "❌ File" in result
        assert "does not exist" in result

        # Test 2: Non-EPUB file
        txt_file = temp_path / "test.txt"
        txt_file.write_text("This is not an epub file")
        result = h.file.rename_epub_file(txt_file)
        assert "❌ File" in result
        assert "is not an EPUB file" in result

        # Test 3: EPUB with complete metadata (author, title, year)
        epub_complete = temp_path / "original.epub"
        create_epub_file(epub_complete, "John Doe", "Test Book", "2023")
        result = h.file.rename_epub_file(epub_complete)
        assert "✅ File renamed:" in result
        expected_name = "Doe John - Test Book - 2023.epub"
        renamed_file = temp_path / expected_name
        assert renamed_file.exists()
        assert not epub_complete.exists()

        # Test 4: EPUB with author and title, no year
        epub_no_year = temp_path / "no_year.epub"
        create_epub_file(epub_no_year, "Jane Smith", "Another Book")
        result = h.file.rename_epub_file(epub_no_year)
        assert "✅ File renamed:" in result
        expected_name = "Smith Jane - Another Book.epub"
        renamed_file = temp_path / expected_name
        assert renamed_file.exists()
        assert not epub_no_year.exists()

        # Test 5: EPUB with multi-part author name
        epub_multi_author = temp_path / "multi_author.epub"
        create_epub_file(epub_multi_author, "Jean Claude Van Damme", "Action Book", "2020")
        result = h.file.rename_epub_file(epub_multi_author)
        assert "✅ File renamed:" in result
        expected_name = "Damme Jean Claude Van - Action Book - 2020.epub"
        renamed_file = temp_path / expected_name
        assert renamed_file.exists()

        # Test 6: EPUB with special characters in metadata
        epub_special = temp_path / "special.epub"
        create_epub_file(epub_special, "Author: Name", "Title/With\\Special*Chars", "2021")
        result = h.file.rename_epub_file(epub_special)
        assert "✅ File renamed:" in result
        # Special characters should be removed
        expected_name = "Name Author - TitleWithSpecialChars - 2021.epub"
        renamed_file = temp_path / expected_name
        assert renamed_file.exists()

        # Test 7: EPUB without metadata (should remain unchanged)
        epub_no_meta = temp_path / "no_metadata.epub"
        create_epub_file(epub_no_meta)
        result = h.file.rename_epub_file(epub_no_meta)
        assert "left unchanged" in result
        assert "📝 File" in result
        assert epub_no_meta.exists()

        # Test 8: EPUB with only title, no author
        epub_title_only = temp_path / "title_only.epub"
        create_epub_file(epub_title_only, title="Solo Title")
        result = h.file.rename_epub_file(epub_title_only)
        assert "left unchanged" in result
        assert "📝 File" in result
        assert epub_title_only.exists()

        # Test 9: EPUB with only author, no title
        epub_author_only = temp_path / "author_only.epub"
        create_epub_file(epub_author_only, author="Solo Author")
        result = h.file.rename_epub_file(epub_author_only)
        assert "left unchanged" in result
        assert "📝 File" in result
        assert epub_author_only.exists()

        # Test 10: File name collision (should add counter)
        epub_collision1 = temp_path / "collision1.epub"
        epub_collision2 = temp_path / "collision2.epub"
        create_epub_file(epub_collision1, "Same Author", "Same Title", "2022")
        create_epub_file(epub_collision2, "Same Author", "Same Title", "2022")

        # Rename first file
        result1 = h.file.rename_epub_file(epub_collision1)
        assert "✅ File renamed:" in result1

        # Rename second file (should get counter)
        result2 = h.file.rename_epub_file(epub_collision2)
        assert "✅ File renamed:" in result2

        # Check both files exist with different names
        expected_name1 = "Author Same - Same Title - 2022.epub"
        expected_name2 = "Author Same - Same Title - 2022 (1).epub"
        assert (temp_path / expected_name1).exists()
        assert (temp_path / expected_name2).exists()

        # Test 11: Invalid year (should be ignored)
        epub_invalid_year = temp_path / "invalid_year.epub"
        create_epub_file(epub_invalid_year, "Test Author", "Test Title", "999")  # Invalid year
        result = h.file.rename_epub_file(epub_invalid_year)
        assert "✅ File renamed:" in result
        expected_name = "Author Test - Test Title.epub"  # No year in filename
        renamed_file = temp_path / expected_name
        assert renamed_file.exists()

        # Test 12: Test with Path object input
        epub_path_input = temp_path / "path_input.epub"
        create_epub_file(epub_path_input, "Path Author", "Path Title", "2024")
        result = h.file.rename_epub_file(epub_path_input)  # Pass Path object
        assert "✅ File renamed:" in result
        expected_name = "Author Path - Path Title - 2024.epub"
        renamed_file = temp_path / expected_name
        assert renamed_file.exists()

        # Test 13: Test with string input
        epub_string_input = temp_path / "string_input.epub"
        create_epub_file(epub_string_input, "String Author", "String Title", "2025")
        result = h.file.rename_epub_file(str(epub_string_input))  # Pass string
        assert "✅ File renamed:" in result
        expected_name = "Author String - String Title - 2025.epub"
        renamed_file = temp_path / expected_name
        assert renamed_file.exists()

        # Test 14: Corrupted EPUB (invalid ZIP)
        corrupted_epub = temp_path / "corrupted.epub"
        corrupted_epub.write_text("This is not a valid ZIP file")
        result = h.file.rename_epub_file(corrupted_epub)
        assert "📝 File" in result
        assert "left unchanged" in result
        assert corrupted_epub.exists()


def test_extract_zip_archive() -> None:
    """Test the extract_zip_archive function with various scenarios."""
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Test 1: Non-existent file
        non_existent = temp_path / "non_existent.zip"
        result = h.file.extract_zip_archive(non_existent)
        assert "❌ File" in result
        assert "does not exist" in result

        # Test 2: Not a file (directory)
        test_dir = temp_path / "test_dir"
        test_dir.mkdir()
        result = h.file.extract_zip_archive(test_dir)
        assert "❌" in result
        assert "is not a file" in result

        # Test 3: Not a ZIP file
        txt_file = temp_path / "test.txt"
        txt_file.write_text("test content")
        result = h.file.extract_zip_archive(txt_file)
        assert "❌" in result
        assert "is not a ZIP file" in result

        # Test 4: Empty ZIP file (corrupted)
        empty_zip = temp_path / "empty.zip"
        empty_zip.write_bytes(b"not a zip file")
        result = h.file.extract_zip_archive(empty_zip)
        assert "❌ Failed to extract" in result
        assert empty_zip.exists()  # File should still exist after failed extraction

        # Test 5: Valid ZIP file with single file
        single_file_zip = temp_path / "single_file.zip"
        with zipfile.ZipFile(single_file_zip, "w") as zf:
            zf.writestr("test_file.txt", "Hello, World!")

        result = h.file.extract_zip_archive(single_file_zip)
        assert "✅ Archive single_file.zip extracted and original file deleted" in result
        assert not single_file_zip.exists()  # Original ZIP should be deleted
        assert (temp_path / "test_file.txt").exists()  # Extracted file should exist
        assert (temp_path / "test_file.txt").read_text() == "Hello, World!"

        # Test 6: Valid ZIP file with multiple files
        multi_file_zip = temp_path / "multi_file.zip"
        with zipfile.ZipFile(multi_file_zip, "w") as zf:
            zf.writestr("file1.txt", "Content 1")
            zf.writestr("file2.txt", "Content 2")
            zf.writestr("subdir/file3.txt", "Content 3")

        result = h.file.extract_zip_archive(multi_file_zip)
        assert "✅ Archive multi_file.zip extracted and original file deleted" in result
        assert not multi_file_zip.exists()  # Original ZIP should be deleted
        assert (temp_path / "file1.txt").exists()
        assert (temp_path / "file2.txt").exists()
        assert (temp_path / "subdir" / "file3.txt").exists()
        assert (temp_path / "file1.txt").read_text() == "Content 1"
        assert (temp_path / "file2.txt").read_text() == "Content 2"
        assert (temp_path / "subdir" / "file3.txt").read_text() == "Content 3"

        # Test 7: ZIP file with nested directory structure
        nested_zip = temp_path / "nested.zip"
        with zipfile.ZipFile(nested_zip, "w") as zf:
            zf.writestr("root_file.txt", "Root content")
            zf.writestr("folder1/file_in_folder1.txt", "Folder1 content")
            zf.writestr("folder1/subfolder/deep_file.txt", "Deep content")
            zf.writestr("folder2/file_in_folder2.txt", "Folder2 content")

        result = h.file.extract_zip_archive(nested_zip)
        assert "✅ Archive nested.zip extracted and original file deleted" in result
        assert not nested_zip.exists()
        assert (temp_path / "root_file.txt").exists()
        assert (temp_path / "folder1" / "file_in_folder1.txt").exists()
        assert (temp_path / "folder1" / "subfolder" / "deep_file.txt").exists()
        assert (temp_path / "folder2" / "file_in_folder2.txt").exists()

        # Test 8: Test with Path object (not string)
        path_test_zip = temp_path / "path_test.zip"
        with zipfile.ZipFile(path_test_zip, "w") as zf:
            zf.writestr("path_test.txt", "Path test content")

        result = h.file.extract_zip_archive(path_test_zip)  # Pass Path object directly
        assert "✅ Archive path_test.zip extracted and original file deleted" in result
        assert not path_test_zip.exists()
        assert (temp_path / "path_test.txt").exists()

        # Test 9: Test with string path
        string_test_zip = temp_path / "string_test.zip"
        with zipfile.ZipFile(string_test_zip, "w") as zf:
            zf.writestr("string_test.txt", "String test content")

        result = h.file.extract_zip_archive(str(string_test_zip))  # Pass string path
        assert "✅ Archive string_test.zip extracted and original file deleted" in result
        assert not string_test_zip.exists()
        assert (temp_path / "string_test.txt").exists()

        # Test 10: Empty ZIP file (valid but empty)
        empty_valid_zip = temp_path / "empty_valid.zip"
        with zipfile.ZipFile(empty_valid_zip, "w") as zf:
            pass  # Create empty but valid ZIP

        result = h.file.extract_zip_archive(empty_valid_zip)
        # Should succeed even with empty ZIP
        assert "✅ Archive empty_valid.zip extracted and original file deleted" in result
        assert not empty_valid_zip.exists()


def test_remove_empty_folders() -> None:
    """Test the remove_empty_folders function with various scenarios."""
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Test 1: Non-existent folder
        non_existent = temp_path / "non_existent"
        result = h.file.remove_empty_folders(non_existent)
        assert "❌ Folder" in result
        assert "does not exist" in result

        # Test 2: Not a directory (file)
        test_file = temp_path / "test.txt"
        test_file.write_text("test content")
        result = h.file.remove_empty_folders(test_file)
        assert "❌" in result
        assert "is not a directory" in result

        # Test 3: Empty root directory
        empty_root = temp_path / "empty_root"
        empty_root.mkdir()
        result = h.file.remove_empty_folders(empty_root)
        assert "📁 No folders found to process" in result

        # Test 4: Directory with no subdirectories
        no_subdirs = temp_path / "no_subdirs"
        no_subdirs.mkdir()
        (no_subdirs / "file.txt").write_text("content")
        result = h.file.remove_empty_folders(no_subdirs)
        assert "📁 No folders found to process" in result

        # Test 5: Single empty folder
        single_empty_root = temp_path / "single_empty_root"
        single_empty_root.mkdir()
        empty_folder = single_empty_root / "empty_folder"
        empty_folder.mkdir()

        result = h.file.remove_empty_folders(single_empty_root)
        assert "✅ Removed 1 empty folder" in result
        assert not empty_folder.exists()
        assert single_empty_root.exists()  # Root should still exist

        # Test 6: Multiple empty folders
        multi_empty_root = temp_path / "multi_empty_root"
        multi_empty_root.mkdir()
        empty1 = multi_empty_root / "empty1"
        empty2 = multi_empty_root / "empty2"
        empty3 = multi_empty_root / "empty3"
        empty1.mkdir()
        empty2.mkdir()
        empty3.mkdir()

        result = h.file.remove_empty_folders(multi_empty_root)
        assert "✅ Removed 3 empty folders" in result
        assert not empty1.exists()
        assert not empty2.exists()
        assert not empty3.exists()

        # Test 7: Nested empty folders
        nested_root = temp_path / "nested_root"
        nested_root.mkdir()
        level1 = nested_root / "level1"
        level2 = level1 / "level2"
        level3 = level2 / "level3"
        level1.mkdir()
        level2.mkdir()
        level3.mkdir()

        result = h.file.remove_empty_folders(nested_root)
        assert "✅ Removed 3 empty folders" in result
        assert not level1.exists()
        assert not level2.exists()
        assert not level3.exists()

        # Test 8: Mixed empty and non-empty folders
        mixed_root = temp_path / "mixed_root"
        mixed_root.mkdir()
        empty_folder = mixed_root / "empty_folder"
        non_empty_folder = mixed_root / "non_empty_folder"
        nested_empty = non_empty_folder / "nested_empty"
        empty_folder.mkdir()
        non_empty_folder.mkdir()
        nested_empty.mkdir()
        (non_empty_folder / "file.txt").write_text("content")

        result = h.file.remove_empty_folders(mixed_root)
        assert "✅ Removed 2 empty folders" in result
        assert not empty_folder.exists()
        assert non_empty_folder.exists()  # Should remain (has file)
        assert not nested_empty.exists()  # Should be removed

        # Test 9: Ignored folders (should not be processed)
        ignored_root = temp_path / "ignored_root"
        ignored_root.mkdir()
        git_folder = ignored_root / ".git"
        pycache_folder = ignored_root / "__pycache__"
        node_modules = ignored_root / "node_modules"
        normal_empty = ignored_root / "normal_empty"

        git_folder.mkdir()
        pycache_folder.mkdir()
        node_modules.mkdir()
        normal_empty.mkdir()

        result = h.file.remove_empty_folders(ignored_root)
        assert "✅ Removed 1 empty folder" in result
        assert git_folder.exists()  # Should remain (ignored)
        assert pycache_folder.exists()  # Should remain (ignored)
        assert node_modules.exists()  # Should remain (ignored)
        assert not normal_empty.exists()  # Should be removed

        # Test 10: Hidden folders with is_ignore_hidden=False
        hidden_root = temp_path / "hidden_root"
        hidden_root.mkdir()
        hidden_empty = hidden_root / ".hidden_empty"
        normal_empty = hidden_root / "normal_empty"
        hidden_empty.mkdir()
        normal_empty.mkdir()

        result = h.file.remove_empty_folders(hidden_root, is_ignore_hidden=False)
        assert "✅ Removed 2 empty folders" in result
        assert not hidden_empty.exists()  # Should be removed
        assert not normal_empty.exists()  # Should be removed

        # Test 11: Additional patterns
        additional_root = temp_path / "additional_root"
        additional_root.mkdir()
        temp_folder = additional_root / "temp"
        logs_folder = additional_root / "logs"
        normal_folder = additional_root / "normal"
        temp_folder.mkdir()
        logs_folder.mkdir()
        normal_folder.mkdir()

        result = h.file.remove_empty_folders(additional_root, additional_patterns=["temp", "logs"])
        assert "✅ Removed 1 empty folder" in result
        assert temp_folder.exists()  # Should remain (ignored by additional pattern)
        assert logs_folder.exists()  # Should remain (ignored by additional pattern)
        assert not normal_folder.exists()  # Should be removed

        # Test 12: Complex nested structure with ignored folders
        complex_root = temp_path / "complex_root"
        complex_root.mkdir()

        # Create structure: complex_root/project/.git/empty_folder
        project = complex_root / "project"
        git_in_project = project / ".git"
        empty_in_git = git_in_project / "empty_folder"
        normal_empty = complex_root / "normal_empty"

        project.mkdir()
        git_in_project.mkdir()
        empty_in_git.mkdir()
        normal_empty.mkdir()

        result = h.file.remove_empty_folders(complex_root)
        assert "✅ Removed 1 empty folder" in result
        assert git_in_project.exists()  # Should remain (ignored)
        assert empty_in_git.exists()  # Should remain (parent is ignored)
        assert not normal_empty.exists()  # Should be removed

        # Test 13: Test with string path (not Path object)
        string_test_root = temp_path / "string_test_root"
        string_test_root.mkdir()
        string_empty = string_test_root / "string_empty"
        string_empty.mkdir()

        result = h.file.remove_empty_folders(str(string_test_root))  # Pass string path
        assert "✅ Removed 1 empty folder" in result
        assert not string_empty.exists()

        # Test 14: Folder that becomes empty after removing nested empty folders
        cascade_root = temp_path / "cascade_root"
        cascade_root.mkdir()
        outer = cascade_root / "outer"
        inner = outer / "inner"
        outer.mkdir()
        inner.mkdir()

        result = h.file.remove_empty_folders(cascade_root)
        assert "✅ Removed 2 empty folders" in result
        assert not outer.exists()  # Should be removed after inner is removed
        assert not inner.exists()  # Should be removed first


def test_rename_files_by_mapping() -> None:
    """Test the rename_files_by_mapping function with various scenarios."""
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test directory structure
        # Root level files
        (temp_path / "old_file.txt").write_text("content1")
        (temp_path / "readme.md").write_text("content2")
        (temp_path / "config.json").write_text("content3")
        (temp_path / "unchanged.txt").write_text("content4")

        # Nested directory with files
        nested_dir = temp_path / "subdir"
        nested_dir.mkdir()
        (nested_dir / "old_file.txt").write_text("nested content1")
        (nested_dir / "another.py").write_text("nested content2")

        # Deeper nested directory
        deep_dir = nested_dir / "deep"
        deep_dir.mkdir()
        (deep_dir / "config.json").write_text("deep content")

        # Directory that should be ignored
        ignored_dir = temp_path / "__pycache__"
        ignored_dir.mkdir()
        (ignored_dir / "old_file.txt").write_text("ignored content")

        # Hidden directory (should be ignored by default)
        hidden_dir = temp_path / ".git"
        hidden_dir.mkdir()
        (hidden_dir / "readme.md").write_text("hidden content")

        # Define rename mapping
        rename_mapping = {"old_file.txt": "new_file.txt", "readme.md": "READMENEW.md", "config.json": "settings.json"}

        # Test 1: Basic functionality
        result = h.file.rename_files_by_mapping(temp_path, rename_mapping)

        # Verify successful renames
        assert "✅ Renamed" in result
        assert "5 files" in result  # Should rename 4 files total

        # Check that files were renamed correctly
        assert (temp_path / "new_file.txt").exists()
        assert (temp_path / "READMENEW.md").exists()
        assert (temp_path / "settings.json").exists()
        assert (nested_dir / "new_file.txt").exists()
        assert (deep_dir / "settings.json").exists()

        # Check that old files no longer exist
        assert not (temp_path / "old_file.txt").exists()
        assert not (temp_path / "readme.md").exists()
        assert not (temp_path / "config.json").exists()
        assert not (nested_dir / "old_file.txt").exists()
        assert not (deep_dir / "config.json").exists()

        # Check that unchanged files still exist
        assert (temp_path / "unchanged.txt").exists()
        assert (nested_dir / "another.py").exists()

        # Check that ignored directories were not processed
        assert (ignored_dir / "old_file.txt").exists()  # Should still exist
        assert (hidden_dir / "readme.md").exists()  # Should still exist

        # Verify content is preserved
        assert (temp_path / "new_file.txt").read_text() == "content1"
        assert (temp_path / "READMENEW.md").read_text() == "content2"
        assert (temp_path / "settings.json").read_text() == "content3"

        # Test 2: File already exists scenario
        # Create a file that would conflict with rename
        (temp_path / "conflict_target.txt").write_text("existing content")
        (temp_path / "conflict_source.txt").write_text("source content")

        result2 = h.file.rename_files_by_mapping(temp_path, {"conflict_source.txt": "conflict_target.txt"})

        # Should skip the rename due to conflict
        assert "skipped" in result2.lower()
        assert (temp_path / "conflict_source.txt").exists()  # Original should still exist
        assert (temp_path / "conflict_target.txt").read_text() == "existing content"  # Target unchanged

        # Test 3: Non-existent directory
        result3 = h.file.rename_files_by_mapping("/non/existent/path", {"a": "b"})
        assert "❌" in result3
        assert "does not exist" in result3

        # Test 4: Empty mapping
        result4 = h.file.rename_files_by_mapping(temp_path, {})
        assert "❌" in result4
        assert "empty" in result4.lower()

        # Test 5: File instead of directory
        test_file = temp_path / "test_file.txt"
        test_file.write_text("test")
        result5 = h.file.rename_files_by_mapping(test_file, {"a": "b"})
        assert "❌" in result5
        assert "not a directory" in result5

        # Test 6: No matching files
        result6 = h.file.rename_files_by_mapping(temp_path, {"nonexistent.txt": "new.txt"})
        assert "No files matched" in result6

        # Test 7: Multiple ignored directories
        # Create more ignored directories
        vscode_dir = temp_path / ".vscode"
        vscode_dir.mkdir()
        (vscode_dir / "old_file.txt").write_text("vscode content")

        node_modules_dir = temp_path / "node_modules"
        node_modules_dir.mkdir()
        (node_modules_dir / "readme.md").write_text("node modules content")

        # These should be ignored
        h.file.rename_files_by_mapping(temp_path, {"old_file.txt": "ignored_test.txt"})
        assert (vscode_dir / "old_file.txt").exists()  # Should still exist (ignored)
        assert (node_modules_dir / "readme.md").exists()  # Should still exist (ignored)

        # Test 8: Single file rename
        single_file_dir = temp_path / "single_test"
        single_file_dir.mkdir()
        (single_file_dir / "single.txt").write_text("single content")

        result8 = h.file.rename_files_by_mapping(single_file_dir, {"single.txt": "renamed_single.txt"})
        assert "✅ Renamed 1 file" in result8
        assert (single_file_dir / "renamed_single.txt").exists()
        assert not (single_file_dir / "single.txt").exists()

        # Test 9: Mixed success and skip scenario
        mixed_dir = temp_path / "mixed_test"
        mixed_dir.mkdir()
        (mixed_dir / "file1.txt").write_text("content1")
        (mixed_dir / "file2.txt").write_text("content2")
        (mixed_dir / "target.txt").write_text("existing target")  # This will cause conflict

        result9 = h.file.rename_files_by_mapping(
            mixed_dir,
            {
                "file1.txt": "renamed1.txt",
                "file2.txt": "target.txt",  # This will be skipped due to conflict
            },
        )

        assert "✅ Renamed 1 file" in result9
        assert "1 were skipped" in result9
        assert (mixed_dir / "renamed1.txt").exists()
        assert (mixed_dir / "file2.txt").exists()  # Should still exist (skipped)
        assert (mixed_dir / "target.txt").read_text() == "existing target"  # Unchanged

        # Test 10: Empty directory
        empty_dir = temp_path / "empty_test"
        empty_dir.mkdir()

        result10 = h.file.rename_files_by_mapping(empty_dir, {"any.txt": "new.txt"})
        assert "No files found to process" in result10

        # Test 11: Directory with only ignored subdirectories
        only_ignored_dir = temp_path / "only_ignored"
        only_ignored_dir.mkdir()
        cache_dir = only_ignored_dir / ".cache"
        cache_dir.mkdir()
        (cache_dir / "test.txt").write_text("cached content")

        result11 = h.file.rename_files_by_mapping(only_ignored_dir, {"test.txt": "new_test.txt"})
        assert "No files found to process" in result11
        assert (cache_dir / "test.txt").exists()  # Should still exist (ignored)
