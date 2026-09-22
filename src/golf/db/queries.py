from src.golf.db.models import Rounds

def get_last_20_rounds(user_id: str) -> list[Rounds]:
    """Retrieves the latest 20 rounds, or all rounds if less than 20 total, for a given user_id

    Args:
        user_id (str): user identifier

    Returns:
        list[Rounds]: list of last 20 rounds (or all if less than 20 total)
    """
    return