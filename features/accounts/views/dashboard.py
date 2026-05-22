from django.shortcuts import render, redirect

from main.auth_utils import get_session_user, login_required
from features.accounts.services import dashboard_service, profile_service


@login_required
def dashboard(request):
    user_email, role = get_session_user(request)

    pengguna = profile_service.get_pengguna(user_email)
    member_data = None
    staf_data = None
    recent_transactions = []
    staff_claim_summary = {'menunggu': 0, 'disetujui': 0, 'ditolak': 0}

    if role == 'member':
        member_data = profile_service.get_member_with_tier(user_email)
        if member_data:
            recent_transactions = dashboard_service.member_recent_transactions(user_email)
    elif role == 'staf':
        staf_data = profile_service.get_staf_with_maskapai(user_email)
        if staf_data:
            staff_claim_summary = dashboard_service.staff_claim_summary(user_email)

    return render(request, 'dashboard.html', {
        'user_email': user_email,
        'role': role,
        'member': member_data,
        'staf': staf_data,
        'pengguna': pengguna,
        'recent_transactions': recent_transactions,
        'staff_claim_summary': staff_claim_summary,
    })
