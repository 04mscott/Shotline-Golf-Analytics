import os

from src.golf.analytics.baselines import get_expected_strokes
from src.golf.analytics.strokes_gained import get_strokes_gained
from src.golf.db.enums import Lie, Skill

import pytest

from tests.sample_strokes import HOLE_YARDAGE, HOLE_SCORE, SKILL

REAL_BASELINE_CSV = os.path.join("data", "baselines", "expected_strokes.csv")


def test_tee_shot(hole_1, fake_baselines):
    """
    End-to-end check: strokes gained on the tee shot, computed directly from
    two get_expected_strokes() calls, should match what get_strokes_gained()
    returns for the same inputs. Uses the fake_baselines fixture so this
    doesn't depend on the real CSV data being present.
    """
    strokes, hole = hole_1
    expected_strokes_start = get_expected_strokes(lie=Lie.TEE, distance=hole.yardage, skill=SKILL)

    tee_shot = strokes[0]
    expected_strokes_end = get_expected_strokes(lie=Lie(tee_shot.lie), distance=tee_shot.distance, skill=SKILL)

    expected_strokes_gained = expected_strokes_start - expected_strokes_end - 1 - tee_shot.penalty_strokes
    strokes_gained = get_strokes_gained(lie1=Lie.TEE, lie2=tee_shot.lie, dist1=hole.yardage, dist2=tee_shot.distance, skill=SKILL)

    assert strokes_gained == pytest.approx(expected_strokes_gained)


def test_full_hole_strokes_gained_telescopes(hole_1, fake_baselines):
    """
    Strokes gained across a full hole should telescope: the sum of
    per-shot strokes gained equals
        (expected strokes from the tee) - (actual total strokes taken),
    since every intermediate expected-strokes term cancels out and the
    final shot compares against 0 (holed).
    """
    strokes, hole = hole_1

    expected_strokes_tee = get_expected_strokes(Lie.TEE, hole.yardage, SKILL)

    total_gained = 0.0
    prev_lie, prev_dist = Lie.TEE, hole.yardage
    for stroke in strokes:
        is_last = stroke.hole_completed and stroke is strokes[-1]
        lie2 = Lie.HOLED if is_last else Lie(stroke.lie)
        dist2 = 0 if is_last else stroke.distance

        total_gained += get_strokes_gained(
            lie1=prev_lie,
            lie2=lie2,
            dist1=prev_dist,
            dist2=dist2,
            skill=SKILL,
            penalty_strokes=stroke.penalty_strokes,
        )
        prev_lie, prev_dist = Lie(stroke.lie), stroke.distance

    actual_total_strokes = len(strokes) + sum(s.penalty_strokes for s in strokes)
    assert total_gained == pytest.approx(expected_strokes_tee - actual_total_strokes)


@pytest.mark.skipif(
    not os.path.exists(REAL_BASELINE_CSV),
    reason="requires the real data/baselines/expected_strokes.csv from the project repo",
)
def test_expected_strokes_real_data():
    """
    Integration test against the *real* baseline CSVs (not mocked). These
    specific numbers come from the project's actual expected-strokes data,
    so this only runs when that data file is present -- e.g. when this test
    suite is run from inside the real project checkout.
    """
    assert get_expected_strokes(Lie.ROUGH, 160, Skill.SCRATCH) == pytest.approx(3.28)
    assert get_expected_strokes(Lie.SAND, 200, Skill.HCP_20) == pytest.approx(4.53)