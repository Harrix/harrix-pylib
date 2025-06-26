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
