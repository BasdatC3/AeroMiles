from django.shortcuts import render, redirect
from django.contrib import messages

from main.auth_utils import get_session_user, role_required
from features.rewards.services import redeem_service


@role_required('member')
def redeem_rewards(request):
    user_email = get_session_user(request)[0]

    if request.method == 'POST':
        kode = (request.POST.get('kode_hadiah') or '').strip()
        if not kode:
            messages.error(request, 'Hadiah tidak valid.')
            return redirect('redeem_rewards')

        hadiah = redeem_service.get_hadiah(kode)
        if not hadiah:
            messages.error(request, 'Hadiah tidak ditemukan.')
            return redirect('redeem_rewards')

        if not redeem_service.is_within_period(hadiah):
            messages.error(request, 'Hadiah di luar periode validitas.')
            return redirect('redeem_rewards')

        member = redeem_service.get_member(user_email)
        if not member or member['award_miles'] < hadiah['miles']:
            messages.error(request, 'Award miles tidak cukup untuk redeem hadiah ini.')
            return redirect('redeem_rewards')

        try:
            redeem_service.execute_redeem(user_email, kode, hadiah['miles'])
            messages.success(request, f"Berhasil redeem '{hadiah['nama']}'.")
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

        return redirect('redeem_rewards')

    return render(request, 'redeem_rewards.html', {
        'rewards': redeem_service.list_active_rewards(),
        'member': redeem_service.get_member(user_email),
        'redeem_history': redeem_service.list_history(user_email),
    })
