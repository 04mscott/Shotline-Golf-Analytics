from src.golf.analytics.baselines import get_expected_strokes
from src.golf.analytics.strokes_gained import get_strokes_gained
from src.golf.db.models import Strokes
from src.golf.analytics.enums import Lie, Skill

import pytest

from tests.sample_strokes import HOLE_YARDAGE, HOLE_SCORE, SKILL

def test_tee_shot(hole_1):
    strokes, hole = hole_1
    expected_strokes_start = get_expected_strokes(lie=Lie.TEE, distance=hole.yardage, skill=SKILL)

    tee_shot = strokes[0]
    expected_strokes_end = get_expected_strokes(lie=Lie(tee_shot.lie), distance=tee_shot.distance, skill=SKILL)

    expected_strokes_gained = expected_strokes_start - expected_strokes_end - 1 - tee_shot.penalty_strokes
    strokes_gained = get_strokes_gained(lie1=Lie.TEE, lie2=tee_shot.lie, dist1=hole.yardage, dist2=tee_shot.distance, skill=SKILL)

    assert strokes_gained == pytest.approx(expected_strokes_gained)


def test_expected_strokes():
    assert get_expected_strokes(Lie.ROUGH, 160, Skill.SCRATCH) == pytest.approx(3.28)
    assert get_expected_strokes(Lie.SAND, 200, Skill.HCP_20) == pytest.approx(4.53)