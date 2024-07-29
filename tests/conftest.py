import pytest


@pytest.fixture
def save_data():
    filepath = 'tests/sample.sav'
    with open(filepath, 'rb') as f:
        return f.read()
