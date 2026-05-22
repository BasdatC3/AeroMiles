from main.db import execute_query


def list_tiers():
    return execute_query(
        "SELECT * FROM tier ORDER BY minimal_tier_miles",
        fetch_all=True,
    ) or []


def get_member(email):
    return execute_query(
        "SELECT * FROM member WHERE email = %s",
        (email,), fetch_one=True,
    )


def annotate_progress(tiers, member):
    """Tandai tier saat ini dan hitung progress ke tier berikutnya."""
    if not member:
        return None, None, 0

    current_id = member['id_tier']
    current_tier = None
    next_tier = None
    miles_to_next = 0

    for idx, t in enumerate(tiers):
        t['is_current'] = (t['id_tier'] == current_id)
        if t['is_current']:
            current_tier = t
            if idx + 1 < len(tiers):
                next_tier = tiers[idx + 1]
                miles_to_next = max(
                    0, next_tier['minimal_tier_miles'] - member['total_miles']
                )

    return current_tier, next_tier, miles_to_next
