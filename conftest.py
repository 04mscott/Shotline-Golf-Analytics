# tests/conftest.py
import pytest
from tests.sample_strokes import make_sample_data

@pytest.fixture
def hole_1():
    return make_sample_data()