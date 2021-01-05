import pytest
from src.main.python.main import make_save_file
import json


@pytest.mark.parametrize(
    "save_path,change_path",
    [
        ("tests/sample_save1.sav", "tests/save_data1.json"),
        ("tests/sample_save2.sav", "tests/save_data2.json"),
        ("tests/sample_save3.sav", "tests/save_data3.json"),
    ],
)
def test_save_changes(save_path, change_path):
    with open(save_path, "rb") as s:
        original_data = s.read()

    with open(change_path, "r") as d:
        sample_changes = json.loads(d.read())

    new_data = make_save_file(save_path, sample_changes)
    assert original_data == new_data
