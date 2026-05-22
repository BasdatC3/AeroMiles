from django.shortcuts import render, redirect
from django.contrib import messages

from main.auth_utils import get_session_user, role_required
from features.transactions.services import transfer_service


@role_required('member')
def transfer_miles(request):
    user_email = get_session_user(request)[0]

    if request.method == "POST":
        to_email = (request.POST.get('to_email') or '').strip()
        jumlah_raw = request.POST.get('jumlah') or ''
        catatan = (request.POST.get('catatan') or '').strip()

        if not to_email or not jumlah_raw:
            messages.error(request, "Email penerima dan jumlah wajib diisi!")
            return redirect('transfer_miles')

        try:
            jumlah = int(jumlah_raw)
        except ValueError:
            messages.error(request, "Jumlah miles harus berupa angka!")
            return redirect('transfer_miles')

        if jumlah <= 0:
            messages.error(request, "Jumlah miles harus lebih dari 0!")
            return redirect('transfer_miles')

        if to_email == user_email:
            messages.error(request, "Tidak bisa transfer ke diri sendiri!")
            return redirect('transfer_miles')

        if not transfer_service.member_exists(to_email):
            messages.error(request, "Email penerima tidak terdaftar sebagai member!")
            return redirect('transfer_miles')

        balance = transfer_service.member_balance(user_email)
        if not balance or balance['award_miles'] < jumlah:
            messages.error(request, "Saldo award miles tidak cukup!")
            return redirect('transfer_miles')

        try:
            transfer_service.execute_transfer(user_email, to_email, jumlah, catatan)
            messages.success(request, "Transfer berhasil!")
        except Exception as e:
            messages.error(request, f"Gagal transfer: {str(e)}")

        return redirect('transfer_miles')

    return render(request, 'transfer_miles.html', {
        'transfers': transfer_service.list_history(user_email),
        'member': transfer_service.member_balance(user_email),
    })
