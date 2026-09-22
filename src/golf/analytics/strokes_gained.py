from src.golf.analytics.baselines import get_expected_strokes
from src.golf.db.enums import Skill, Lie

def get_strokes_gained(
        lie1: Lie | str,
        lie2: Lie | str,
        dist1: int,
        dist2: int,
        skill: Skill | str,
        penalty_strokes: int = 0
) -> float:
    """_summary_

    Args:
        lie1 (Lie): Starting lie
        lie2 (Lie): Ending Lie
        dist1 (int): Starting distance to hole
        dist2 (int): Ending distance to hole
        skill (Skill): Skill level of user
        penalty_strokes (int, optional): Penalty strokes resulting from the stroke. Defaults to 0.

    Returns:
        float: Strokes Gained (unrounded)
    """
    expected_strokes_start = get_expected_strokes(lie1, dist1, skill)
    if dist2 == 0 and lie2 == Lie.HOLED:
        expected_strokes_end = 0
    else:
        expected_strokes_end = get_expected_strokes(lie2, dist2, skill)

    return expected_strokes_start - expected_strokes_end - 1 - penalty_strokes