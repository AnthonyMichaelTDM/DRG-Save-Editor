import pytest
from src.main.python.main import get_xp, make_save_file
import json

# import struct


# with open('tests/sample_save.sav', 'rb') as s:
#     save_data = s.read()


@pytest.mark.parametrize(
    "save_path,xp_dict,passing_test",
    [
        (
            "tests/sample_save.sav",
            {
                "driller": {"xp": 282753, "promo": 2},
                "gunner": {"xp": 13186, "promo": 1},
                "scout": {"xp": 301821, "promo": 1},
                "engineer": {"xp": 0, "promo": 1},
            },
            True,
        ),
        (
            "tests/sample_save.sav",
            {
                "this": "test should fail",
            },
            False,
        ),
    ],
)
def test_get_xp(save_path, xp_dict, passing_test):
    with open(save_path, "rb") as s:
        save_bytes = s.read()

    if passing_test:
        assert get_xp(save_bytes) == xp_dict
    else:
        assert get_xp(save_bytes) != xp_dict


with open("tests/dummy_save_data.json", "r") as d:
    sample_changes = json.loads(d.read())


@pytest.mark.parametrize(
    "save_path,change_data", [("tests/sample_save.sav", sample_changes)]
)
def test_save_changes(save_path, change_data):
    with open(save_path, "rb") as s:
        original_data = s.read()

    new_data = make_save_file(save_path, change_data)
    assert original_data == new_data
