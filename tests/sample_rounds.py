from decimal import Decimal, ROUND_HALF_UP
import datetime

from src.golf.db.models import Tees, Rounds

def make_sample_rounds_data() -> tuple[Tees, list[Rounds]]:
    # ---- Tee that all 20 rounds were played on ----
    tee = Tees(
        id=1,
        course_id=1,
        name="White",
        gender="M",
        course_rating=Decimal("71.2"),
        slope_rating=128,
    )

    def differential(agp: Decimal, cr: Decimal, slope: int) -> Decimal:
        raw = (agp - cr) * Decimal("113") / Decimal(slope)
        return raw.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

    CR = tee.course_rating
    SLOPE = tee.slope_rating

    # Adjusted Gross Scores (AGS) — i.e., already after any NDB capping applied hole-by-hole.
    # For most rounds this equals actual gross score. For rounds #7 and #14, the golfer
    # blew up on a hole and the score shown is capped at Net Double Bogey for a ~20 handicap
    # player (par + 2 + handicap strokes on that hole), not the real strokes taken.
    round_data = [
        # (played_on, AGS, holes_played, note)
        ("2025-03-02", Decimal("94"), "18", None),
        ("2025-03-09", Decimal("91"), "18", None),
        ("2025-03-16", Decimal("96"), "18", None),
        ("2025-03-23", Decimal("89"), "18", None),
        ("2025-03-30", Decimal("93"), "18", None),
        ("2025-04-06", Decimal("90"), "18", None),
        ("2025-04-13", Decimal("97"), "18",
            "Real score 12 on hole 5 (par 4, SI 2) capped to NDB max of 7"),
        ("2025-04-20", Decimal("92"), "18", None),
        ("2025-04-27", Decimal("88"), "18", None),
        ("2025-05-04", Decimal("95"), "18", None),
        ("2025-05-11", Decimal("91"), "18", None),
        ("2025-05-18", Decimal("87"), "18", None),
        ("2025-05-25", Decimal("94"), "18", None),
        ("2025-06-01", Decimal("99"), "18",
            "Real score 11 on hole 12 (par 3, SI 15) capped to NDB max of 6"),
        ("2025-06-08", Decimal("90"), "18", None),
        ("2025-06-15", Decimal("93"), "18", None),
        ("2025-06-22", Decimal("89"), "18", None),
        ("2025-06-29", Decimal("92"), "18", None),
        ("2025-07-06", Decimal("96"), "18", None),
        ("2025-07-13", Decimal("88"), "18", None),
    ]

    rounds = []
    for played_on, ags, holes_played, note in round_data:
        diff = differential(ags, CR, SLOPE)
        rounds.append(Rounds(
            user_id=1,
            tee_id=tee.id,
            played_on=datetime.date.fromisoformat(played_on),
            holes_played=holes_played,
            counts_for_handicap=True,
            differential=diff,
            notes=note,
        ))

    return tee, rounds