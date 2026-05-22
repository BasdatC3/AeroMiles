from django.shortcuts import render, redirect
from django.contrib import messages

from main.auth_utils import get_session_user, role_required
from features.rewards.services import package_service


@role_required('member')
def buy_packages(request):
    user_email = get_session_user(request)[0]

    if request.method == 'POST':
        package_id = (request.POST.get('package_id') or '').strip()
        if not package_id:
            messages.error(request, 'Paket tidak valid.')
            return redirect('buy_packages')

        package = package_service.get(package_id)
        if not package:
            messages.error(request, 'Paket tidak ditemukan.')
            return redirect('buy_packages')

        try:
            package_service.execute_purchase(
                user_email, package_id, package['jumlah_award_miles'],
            )
            messages.success(
                request,
                f"Berhasil membeli paket {package_id} (+{package['jumlah_award_miles']} miles).",
            )
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

        return redirect('buy_packages')

    return render(request, 'buy_packages.html', {
        'packages': package_service.list_all(),
        'member': package_service.get_member(user_email),
        'purchase_history': package_service.list_purchases(user_email),
    })
