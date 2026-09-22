"""
Unit tests for get_strokes_gained() in isolation.

These mock out get_expected_strokes entirely, so they test only the
strokes-gained *formula* -- not the baseline lookup/interpolation, which is
covered separately in test_baselines.py.
"""
import pytest

from src.golf.analytics import strokes_gained as strokes_gained_module
from src.golf.db.enums import Lie, Skill
from src.golf.analytics.strokes_gained import get_strokes_gained


@pytest.fixture
def mock_expected_strokes(mocker):
    """
    Patches get_expected_strokes (as imported into strokes_gained.py) to
    return values from a simple lookup table keyed by (lie, distance),
    ignoring skill. Lets each test spell out exactly what it wants each
    call to return.
    """
    def _install(table):
        def fake(lie, distance, skill):
            return table[(lie, distance)]

        return mocker.patch.object(strokes_gained_module, "get_expected_strokes", side_effect=fake)

    return _install


class TestGetStrokesGained:
    def test_basic_formula(self, mock_expected_strokes):
        mock = mock_expected_strokes({
            (Lie.FAIRWAY, 150): 3.0,
            (Lie.GREEN, 20): 1.8,
        })
        result = get_strokes_gained(
            lie1=Lie.FAIRWAY, lie2=Lie.GREEN, dist1=150, dist2=20, skill=Skill.SCRATCH
        )
        # 3.0 - 1.8 - 1 (this stroke) - 0 (no penalty)
        assert result == pytest.approx(0.2)
        assert mock.call_count == 2

    def test_penalty_strokes_are_subtracted(self, mock_expected_strokes):
        mock_expected_strokes({
            (Lie.FAIRWAY, 150): 3.0,
            (Lie.ROUGH, 100): 2.8,
        })
        result = get_strokes_gained(
            lie1=Lie.FAIRWAY, lie2=Lie.ROUGH, dist1=150, dist2=100,
            skill=Skill.SCRATCH, penalty_strokes=1,
        )
        # 3.0 - 2.8 - 1 - 1 penalty
        assert result == pytest.approx(-1.8)

    def test_default_penalty_is_zero(self, mock_expected_strokes):
        mock_expected_strokes({
            (Lie.FAIRWAY, 150): 3.0,
            (Lie.ROUGH, 100): 2.8,
        })
        # Omitting penalty_strokes should behave the same as passing 0.
        with_default = get_strokes_gained(Lie.FAIRWAY, Lie.ROUGH, 150, 100, Skill.SCRATCH)
        with_explicit_zero = get_strokes_gained(Lie.FAIRWAY, Lie.ROUGH, 150, 100, Skill.SCRATCH, penalty_strokes=0)
        assert with_default == pytest.approx(with_explicit_zero)

    def test_holed_shortcut_skips_lookup_and_treats_end_as_zero(self, mock_expected_strokes):
        mock = mock_expected_strokes({
            (Lie.GREEN, 3): 1.4,
        })
        result = get_strokes_gained(
            lie1=Lie.GREEN, lie2=Lie.HOLED, dist1=3, dist2=0, skill=Skill.SCRATCH
        )
        # 1.4 - 0 - 1 - 0
        assert result == pytest.approx(0.4)
        # Only the *starting* lookup should happen -- the ending lookup is
        # skipped entirely for a holed putt.
        assert mock.call_count == 1

    def test_holed_requires_both_distance_zero_and_lie_holed(self, mock_expected_strokes):
        # If dist2 is 0 but lie2 isn't HOLED, this should NOT take the
        # shortcut -- it should still look up expected strokes for lie2.
        mock = mock_expected_strokes({
            (Lie.GREEN, 3): 1.4,
            (Lie.GREEN, 0): 2.0,  # nonsensical value, just to prove it's used
        })
        result = get_strokes_gained(
            lie1=Lie.GREEN, lie2=Lie.GREEN, dist1=3, dist2=0, skill=Skill.SCRATCH
        )
        assert result == pytest.approx(1.4 - 2.0 - 1)
        assert mock.call_count == 2

    def test_negative_strokes_gained_for_a_poor_shot(self, mock_expected_strokes):
        # Moving to a *worse* expected position than where you started
        # (net of the stroke spent) should yield a negative value.
        mock_expected_strokes({
            (Lie.FAIRWAY, 150): 3.0,
            (Lie.SAND, 140): 3.4,
        })
        result = get_strokes_gained(Lie.FAIRWAY, Lie.SAND, 150, 140, Skill.HCP_15)
        assert result < 0

    def test_accepts_plain_string_lies(self, mock_expected_strokes):
        mock_expected_strokes({
            ("fairway", 150): 3.0,
            ("rough", 100): 2.8,
        })
        result = get_strokes_gained("fairway", "rough", 150, 100, Skill.SCRATCH)
        assert result == pytest.approx(-0.8)