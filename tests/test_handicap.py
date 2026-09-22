from decimal import Decimal

from src.golf.db.models import Tees, Rounds
from src.golf.analytics.handicap import get_handicap_index

def test_handicap(sample_rounds):
    tee, rounds = sample_rounds
    assert get_handicap_index([r.differential for r in rounds]) == Decimal("15.1")