"""
Shared pytest fixtures for the strokes-gained analytics test suite.
"""
import pandas as pd
import pytest

from src.golf.analytics import baselines as baselines_module
from src.golf.db.enums import Lie, Skill
from tests.sample_strokes import make_sample_data
from tests.sample_rounds import make_sample_rounds_data


# ---------------------------------------------------------------------------
# Cache hygiene
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _clear_baselines_cache():
    baselines_module.get_baselines.cache_clear()
    yield
    baselines_module.get_baselines.cache_clear()


# ---------------------------------------------------------------------------
# Fake baseline data
# ---------------------------------------------------------------------------
ALL_SKILLS = list(Skill)


def _skill_row(base_by_skill):
    """Fill in any Skill not explicitly given using the nearest neighbor,
    just so every column is present with a plausible number."""
    return {skill: base_by_skill.get(skill, next(iter(base_by_skill.values()))) for skill in ALL_SKILLS}


FAIRWAY_YARDS = [100, 150, 200]
FAIRWAY_ES = _skill_row({
    Skill.SCRATCH: [2.5, 3.0, 3.5],
    Skill.HCP_15: [3.0, 3.5, 4.0],
    Skill.HCP_20: [3.2, 3.7, 4.2],
})

ROUGH_YARDS = [100, 150, 200]
ROUGH_ES = _skill_row({
    Skill.SCRATCH: [2.7, 3.28, 3.7],
    Skill.HCP_15: [3.2, 3.7, 4.2],
    Skill.HCP_20: [3.4, 3.9, 4.4],
})

SAND_YARDS = [100, 150, 200]
SAND_ES = _skill_row({
    Skill.SCRATCH: [2.9, 3.4, 3.9],
    Skill.HCP_15: [3.4, 3.9, 4.4],
    Skill.HCP_20: [3.6, 4.1, 4.53],
})

TEE_YARDS = [300, 350, 400]
TEE_ES = _skill_row({
    Skill.HCP_15: [3.9, 4.1, 4.3],
})

GREEN_FEET = [1, 5, 10, 20]
GREEN_ES = _skill_row({
    Skill.SCRATCH: [1.0, 1.5, 1.8, 2.0],
    Skill.HCP_15: [1.05, 1.6, 1.95, 2.2],
    Skill.HCP_20: [1.08, 1.65, 2.0, 2.3],
})


@pytest.fixture
def fake_baselines(monkeypatch):
    """
    Replace pd.read_csv (as seen from the baselines module) with fixed,
    hand-computed lookup tables, so get_expected_strokes can be tested
    against exact arithmetic instead of real ShotLink data.
    """
    def _build_df(yards, lie, es_by_skill):
        row_base = {"yards": yards, "lie": [lie] * len(yards)}
        for skill, values in es_by_skill.items():
            row_base[skill] = values
        return pd.DataFrame(row_base)

    fairway_df = _build_df(FAIRWAY_YARDS, Lie.FAIRWAY, FAIRWAY_ES)
    rough_df = _build_df(ROUGH_YARDS, Lie.ROUGH, ROUGH_ES)
    sand_df = _build_df(SAND_YARDS, Lie.SAND, SAND_ES)
    tee_df = _build_df(TEE_YARDS, Lie.TEE, TEE_ES)

    expected_strokes_df = pd.concat(
        [fairway_df, rough_df, sand_df, tee_df], ignore_index=True
    )

    green_row_base = {"feet": GREEN_FEET}
    for skill, values in GREEN_ES.items():
        green_row_base[skill] = values
    expected_strokes_green_df = pd.DataFrame(green_row_base)

    def fake_read_csv(path, *args, **kwargs):
        if "green" in path:
            return expected_strokes_green_df.copy()
        return expected_strokes_df.copy()

    monkeypatch.setattr(baselines_module.pd, "read_csv", fake_read_csv)
    return {
        "fairway": FAIRWAY_ES,
        "rough": ROUGH_ES,
        "sand": SAND_ES,
        "tee": TEE_ES,
        "green": GREEN_ES,
        "green_feet": GREEN_FEET,
        "fairway_yards": FAIRWAY_YARDS,
        "rough_yards": ROUGH_YARDS,
        "sand_yards": SAND_YARDS,
        "tee_yards": TEE_YARDS,
    }


# ---------------------------------------------------------------------------
# Hole fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def hole_1():
    """
    (strokes, hole) for a single sample hole, as used by
    test_strokes_gained.test_tee_shot.
    """
    strokes, hole = make_sample_data()
    return strokes, hole


# ---------------------------------------------------------------------------
# Round fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def sample_rounds():
    tee, rounds = make_sample_rounds_data()
    return tee, rounds