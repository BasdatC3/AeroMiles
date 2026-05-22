from django.shortcuts import render

from main.auth_utils import get_session_user
from features.rewards.services import tier_service


def tier_info(request):
    user_email, role = get_session_user(request)
    tiers = tier_service.list_tiers()

    member = None
    current_tier = None
    next_tier = None
    miles_to_next = 0

    if user_email and role == 'member':
        member = tier_service.get_member(user_email)
        current_tier, next_tier, miles_to_next = tier_service.annotate_progress(
            tiers, member,
        )

    return render(request, 'tier_info.html', {
        'tiers': tiers,
        'member': member,
        'current_tier': current_tier,
        'next_tier': next_tier,
        'miles_to_next': miles_to_next,
    })
