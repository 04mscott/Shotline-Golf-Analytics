from src.golf.db.enums import Skill, Lie

from functools import cache

import pandas as pd
import numpy as np


@cache
def get_baselines() -> dict:
    """Loads baseline expected strokes data from CSV

    Returns:
        dict: Baseline expected strokes lookup dictionary
    """
    expected_strokes_df = pd.read_csv('data/baselines/expected_strokes.csv')
    expected_strokes_green_df = pd.read_csv('data/baselines/expected_strokes_(green).csv')

    baselines = {}

    for skill in Skill:
        for lie in set(expected_strokes_df['lie'].tolist()):
            baselines[lie, skill] = expected_strokes_df[expected_strokes_df['lie'] == lie]['yards'].tolist(), expected_strokes_df[expected_strokes_df['lie'] == lie][skill].tolist()
            baselines['green', skill] = expected_strokes_green_df['feet'].tolist(), expected_strokes_green_df[skill].tolist()

    return baselines

def get_expected_strokes(lie: Lie | str, distance: int, skill: Skill | str) -> float:
    """Returns an expected strokes value, either pulled directly from the lookup dict or lineraly interpolated

    Args:
        lie (Lie): Lie of the golf ball
        distance (int): Distance to the hole in yards (unless Lie.GREEN, then feet)
        skill (Skill): Skill level of the user

    Returns:
        float: Expected strokes from the given Lie/Distance combination, at the users skill level
    """
    baselines = get_baselines()
    distances, es = baselines[(lie, skill)]
    if lie == Lie.GREEN:
        distance = np.log(distance) if distance >= 1 else np.log(1)
        distances = np.log(distances)
    return float(np.interp(distance, distances, es))