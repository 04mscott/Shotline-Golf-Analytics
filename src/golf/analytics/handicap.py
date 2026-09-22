from decimal import Decimal, ROUND_HALF_UP

def get_handicap_index(differentials: list[Decimal]) -> Decimal:
    lowest_8 = sorted(differentials)[:8]
    avg = sum(lowest_8) / len(lowest_8)
    idx = avg * Decimal("0.96")
    return idx.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    