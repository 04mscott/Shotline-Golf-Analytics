from src.golf.db.models import Strokes, Holes
from src.golf.analytics.enums import Skill

ROUND_ID = 1
HOLE_NUM = 1

SKILL = Skill.HCP_15

TEE_ID = 1
PAR = 4
HOLE_YARDAGE = 353
STROKE_INDEX = 11

def make_sample_data() -> tuple:
    return (
        [
            # Shot one end result - Hooked 5 iron off the tee
            Strokes(round_id=ROUND_ID, hole_num=HOLE_NUM, stroke_num=1,
                    lie="rough", distance=75, penalty_strokes=0,
                    hole_completed=True, miss_type="hook"),
            # Shot two end result - Topped approach into hazard
            Strokes(round_id=ROUND_ID, hole_num=HOLE_NUM, stroke_num=2,
                    lie="rough", distance=65, penalty_strokes=1,
                    hole_completed=True, miss_type="top"),
            # Shot three end result - Got onto the green
            Strokes(round_id=ROUND_ID, hole_num=HOLE_NUM, stroke_num=3,
                    lie="green", distance=20, penalty_strokes=0,
                    hole_completed=True),
            # Shot four end result - Hammered putt passed the hole
            Strokes(round_id=ROUND_ID, hole_num=HOLE_NUM, stroke_num=4,
                    lie="green", distance=5, penalty_strokes=0,
                    hole_completed=True, miss_depth="long"),
            # Shot 5 end result - Left putt short
            Strokes(round_id=ROUND_ID, hole_num=HOLE_NUM, stroke_num=5,
                    lie="green", distance=1, penalty_strokes=0,
                    hole_completed=True, miss_depth="short"),
        ],
        Holes(tee_id=TEE_ID, hole_num=HOLE_NUM, par=PAR, yardage=HOLE_YARDAGE, stroke_index=STROKE_INDEX),
    )

strokes = make_sample_data()[0]
HOLE_SCORE = sum(1 + s.penalty_strokes for s in strokes) + 1