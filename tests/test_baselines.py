"""
Unit tests for src.golf.analytics.baselines.

These tests never touch the real data/baselines/*.csv files -- they use the
`fake_baselines` fixture (see conftest.py) to substitute small, hand-picked
lookup tables so every assertion can be verified by hand. That keeps these
tests fast, deterministic, and independent of whatever numbers happen to be
in the real ShotLink-derived CSVs.

For a test that exercises the *real* CSV data, see test_expected_strokes_real_data
in test_strokes_gained.py.
"""
import math

import numpy as np
import pandas as pd
import pytest

from src.golf.analytics.baselines import get_baselines, get_expected_strokes
from src.golf.db.enums import Lie, Skill


class TestGetBaselines:
    def test_loads_and_shapes_data(self, fake_baselines):
        baselines = get_baselines()

        distances, es = baselines[(Lie.FAIRWAY, Skill.SCRATCH)]
        assert list(distances) == fake_baselines["fairway_yards"]
        assert list(es) == fake_baselines["fairway"][Skill.SCRATCH]

    def test_green_lookup_uses_feet_not_yards(self, fake_baselines):
        baselines = get_baselines()

        distances, es = baselines[(Lie.GREEN, Skill.SCRATCH)]
        assert list(distances) == fake_baselines["green_feet"]
        assert list(es) == fake_baselines["green"][Skill.SCRATCH]

    def test_result_is_cached(self, fake_baselines, monkeypatch):
        calls = {"n": 0}
        import src.golf.analytics.baselines as baselines_module

        original_read_csv = baselines_module.pd.read_csv

        def counting_read_csv(*args, **kwargs):
            calls["n"] += 1
            return original_read_csv(*args, **kwargs)

        monkeypatch.setattr(baselines_module.pd, "read_csv", counting_read_csv)

        get_baselines.cache_clear()
        get_baselines()
        get_baselines()
        get_baselines()

        # Two files are read on the *first* call only; later calls are served
        # from the @cache decorator.
        assert calls["n"] == 2

    def test_string_and_enum_keys_are_interchangeable(self, fake_baselines):
        # Lie/Skill are StrEnum, so a plain string key should hit the same
        # dict entry as the enum member.
        baselines = get_baselines()
        assert baselines[(Lie.FAIRWAY, Skill.SCRATCH)] == baselines[("fairway", "scratch")]


class TestGetExpectedStrokes:
    def test_exact_grid_point_non_green(self, fake_baselines):
        # 150 is an exact x-value in the fake fairway/scratch table -> 3.0
        result = get_expected_strokes(Lie.FAIRWAY, 150, Skill.SCRATCH)
        assert result == pytest.approx(3.0)

    def test_linear_interpolation_between_grid_points(self, fake_baselines):
        # Fairway/scratch: 100 -> 2.5, 150 -> 3.0. Midpoint (125) should be
        # the arithmetic mean since the two anchor points are evenly spaced.
        result = get_expected_strokes(Lie.FAIRWAY, 125, Skill.SCRATCH)
        assert result == pytest.approx(2.75)

    def test_interpolation_off_center(self, fake_baselines):
        # Fairway/scratch: 150 -> 3.0, 200 -> 3.5. At 180 (60% of the way):
        # 3.0 + 0.6 * (3.5 - 3.0) = 3.3
        result = get_expected_strokes(Lie.FAIRWAY, 180, Skill.SCRATCH)
        assert result == pytest.approx(3.3)

    def test_distance_below_min_clamps_to_first_value(self, fake_baselines):
        # np.interp holds the boundary value flat outside the known range.
        result = get_expected_strokes(Lie.FAIRWAY, 10, Skill.SCRATCH)
        assert result == pytest.approx(2.5)

    def test_distance_above_max_clamps_to_last_value(self, fake_baselines):
        result = get_expected_strokes(Lie.FAIRWAY, 999, Skill.SCRATCH)
        assert result == pytest.approx(3.5)

    def test_accepts_plain_strings_for_lie_and_skill(self, fake_baselines):
        via_enum = get_expected_strokes(Lie.ROUGH, 150, Skill.HCP_15)
        via_string = get_expected_strokes("rough", 150, "15 handicap")
        assert via_enum == pytest.approx(via_string)

    def test_tee_lie(self, fake_baselines):
        result = get_expected_strokes(Lie.TEE, 350, Skill.HCP_15)
        assert result == pytest.approx(4.1)

    def test_sand_lie(self, fake_baselines):
        result = get_expected_strokes(Lie.SAND, 200, Skill.HCP_20)
        assert result == pytest.approx(4.53)

    # -- GREEN is special-cased: it's keyed by feet, not yards, and
    #    interpolated on a log scale rather than linearly. --

    def test_green_exact_grid_point(self, fake_baselines):
        result = get_expected_strokes(Lie.GREEN, 10, Skill.SCRATCH)
        assert result == pytest.approx(1.8)

    def test_green_uses_log_scale_interpolation(self, fake_baselines):
        # Green/scratch grid: 5ft -> 1.5, 10ft -> 1.8 (feet given, but
        # interpolation happens in log-space).
        distance = 7
        expected = np.interp(math.log(distance), np.log([5, 10]), [1.5, 1.8])
        result = get_expected_strokes(Lie.GREEN, distance, Skill.SCRATCH)
        assert result == pytest.approx(float(expected))
        # Sanity check this genuinely differs from naive linear interpolation.
        naive_linear = 1.5 + (distance - 5) / (10 - 5) * (1.8 - 1.5)
        assert result != pytest.approx(naive_linear)

    def test_green_distance_below_one_clamps_to_one(self, fake_baselines):
        # distance < 1 should behave identically to distance == 1
        # (both map to log(1) == 0 internally).
        at_one = get_expected_strokes(Lie.GREEN, 1, Skill.SCRATCH)
        at_zero_point_five = get_expected_strokes(Lie.GREEN, 0.5, Skill.SCRATCH)
        assert at_zero_point_five == pytest.approx(at_one)

    def test_unknown_lie_skill_combo_raises_keyerror(self, fake_baselines):
        with pytest.raises(KeyError):
            get_expected_strokes(Lie.RECOVERY, 100, Skill.SCRATCH)