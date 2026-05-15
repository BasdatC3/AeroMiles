from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from main.db import execute_query, execute_write
from features.accounts.views import get_user_from_request as get_session_user


def claim_miles(request):
    user_email, role = get_session_user(request)

    if request.method == "POST":
        flight_number = request.POST.get('flight_number')

        if not flight_number:
            messages.error(request, "Flight number wajib diisi!")
            return redirect('claim_miles')

        try:
            execute_write(
                """INSERT INTO claim_missing_miles
                   (email_member, maskapai, bandara_asal, bandara_tujuan, tanggal_penerbangan,
                    flight_number, nomor_tiket, kelas_kabin, pnr, status_penerimaan, timestamp)
                   VALUES (%s, 'GA', 'CGK', 'DPS', CURRENT_DATE, %s, 'AUTO', 'Economy', 'AUTO', 'Menunggu', CURRENT_TIMESTAMP)""",
                (user_email, flight_number)
            )
            messages.success(request, "Klaim berhasil diajukan!")

        except Exception as e:
            messages.error(request, f"Gagal klaim: {str(e)}")

        return redirect('claim_miles')

    claims = execute_query(
        """SELECT * FROM claim_missing_miles
           WHERE email_member = %s
           ORDER BY timestamp DESC""",
        (user_email,),
        fetch_all=True
    ) or []

    return render(request, 'claim_miles.html', {'claims': claims})


def transfer_miles(request):
    user_email, role = get_session_user(request)

    if request.method == "POST":
        to_email = request.POST.get('to_email')
        jumlah = request.POST.get('jumlah')

        if not to_email or not jumlah:
            messages.error(request, "Semua field wajib diisi!")
            return redirect('transfer_miles')

        jumlah = int(jumlah)

        if to_email == user_email:
            messages.error(request, "Tidak bisa transfer ke diri sendiri!")
            return redirect('transfer_miles')

        try:
            saldo = execute_query(
                "SELECT award_miles FROM member WHERE email = %s",
                (user_email,),
                fetch_one=True
            )

            if not saldo or saldo['award_miles'] < jumlah:
                messages.error(request, "Saldo tidak cukup!")
                return redirect('transfer_miles')

            execute_write(
                "UPDATE member SET award_miles = award_miles - %s WHERE email = %s",
                (jumlah, user_email)
            )

            execute_write(
                "UPDATE member SET award_miles = award_miles + %s WHERE email = %s",
                (jumlah, to_email)
            )

            execute_write(
                """INSERT INTO transfer (email_member_1, email_member_2, jumlah, catatan, timestamp)
                   VALUES (%s, %s, %s, 'Transfer', CURRENT_TIMESTAMP)""",
                (user_email, to_email, jumlah)
            )

            messages.success(request, "Transfer berhasil!")

        except Exception as e:
            messages.error(request, f"Gagal transfer: {str(e)}")

        return redirect('transfer_miles')

    transfers = execute_query(
        """SELECT * FROM transfer
           WHERE email_member_1 = %s
           ORDER BY timestamp DESC""",
        (user_email,),
        fetch_all=True
    ) or []

    return render(request, 'transfer_miles.html', {'transfers': transfers})


def manage_claims(request):
    status_filter = request.GET.get('status')

    query = "SELECT * FROM claim_missing_miles"
    params = []
    if status_filter:
        query += " WHERE status_penerimaan = %s"
        params.append(status_filter)
    query += " ORDER BY timestamp DESC"

    claims = execute_query(query, params, fetch_all=True) or []

    return render(request, 'manage_claims.html', {
        'claims': claims,
        'status_filter': status_filter,
    })


@require_POST
def approve_claim(request, id):
    user_email, _ = get_session_user(request)

    execute_write(
        """UPDATE claim_missing_miles
           SET status_penerimaan = 'Disetujui', email_staf = %s
           WHERE id = %s""",
        (user_email, id)
    )

    return redirect('manage_claims')


@require_POST
def reject_claim(request, id):
    user_email, _ = get_session_user(request)

    execute_write(
        """UPDATE claim_missing_miles
           SET status_penerimaan = 'Ditolak', email_staf = %s
           WHERE id = %s""",
        (user_email, id)
    )

    return redirect('manage_claims')


def transaction_report(request):
    total_members = execute_query("SELECT COUNT(*) as cnt FROM member", fetch_one=True)
    total_members = total_members['cnt'] if total_members else 0

    total_claims = execute_query("SELECT COUNT(*) as cnt FROM claim_missing_miles", fetch_one=True)
    total_claims = total_claims['cnt'] if total_claims else 0

    pending_claims = execute_query(
        "SELECT COUNT(*) as cnt FROM claim_missing_miles WHERE status_penerimaan = 'Menunggu'",
        fetch_one=True
    )
    pending_claims = pending_claims['cnt'] if pending_claims else 0

    approved_claims = execute_query(
        "SELECT COUNT(*) as cnt FROM claim_missing_miles WHERE status_penerimaan = 'Disetujui'",
        fetch_one=True
    )
    approved_claims = approved_claims['cnt'] if approved_claims else 0

    rejected_claims = execute_query(
        "SELECT COUNT(*) as cnt FROM claim_missing_miles WHERE status_penerimaan = 'Ditolak'",
        fetch_one=True
    )
    rejected_claims = rejected_claims['cnt'] if rejected_claims else 0

    claims = execute_query(
        "SELECT * FROM claim_missing_miles ORDER BY timestamp DESC",
        fetch_all=True
    ) or []

    transfers = execute_query(
        "SELECT * FROM transfer ORDER BY timestamp DESC",
        fetch_all=True
    ) or []

    total_redeems = execute_query("SELECT COUNT(*) as cnt FROM redeem", fetch_one=True)
    total_redeems = total_redeems['cnt'] if total_redeems else 0

    return render(request, 'transaction_report.html', {
        'total_members': total_members,
        'total_claims': total_claims,
        'pending_claims': pending_claims,
        'approved_claims': approved_claims,
        'rejected_claims': rejected_claims,
        'claims': claims,
        'transfers': transfers,
        'total_redeems': total_redeems,
    })