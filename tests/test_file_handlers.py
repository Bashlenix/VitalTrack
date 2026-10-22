import pytest

from utils.file_handlers import allowed_file, generate_unique_filename


@pytest.mark.parametrize(
    "filename, expected",
    [("scan.PNG", True), ("scan.dcm", True), ("malware.exe", False), ("noext", False)],
)
def test_allowed_file(app, filename, expected):
    assert allowed_file(filename) is expected


def test_unique_filename_keeps_lowercased_extension():
    assert generate_unique_filename("scan.JPG").endswith(".jpg")


def test_unique_filename_differs_per_call():
    assert generate_unique_filename("a.png") != generate_unique_filename("a.png")


def test_unique_filename_rejects_empty_name():
    assert generate_unique_filename("") is None
