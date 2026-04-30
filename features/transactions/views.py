from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection


def get_user_from_request(request):
    return request.session.get('user_email'), request.session.get('user_role')

def claim_miles(request):
    user_email, role = get_user_from_request(request)
    from features.accounts.models import ClaimMissingMiles

    if request.method == "POST":
        flight_number = request.POST.get('flight_number')

        if not flight_number:
            messages.error(request, "Flight number wajib diisi!")
            return redirect('claim_miles')

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO CLAIM_MISSING_MILES 
                    (email_member, maskapai, bandara_asal, bandara_tujuan, tanggal_penerbangan, flight_number, nomor_tiket, kelas_kabin, pnr)
                    VALUES (%s, 'GA', 'CGK', 'DPS', CURRENT_DATE, %s, 'AUTO', 'Economy', 'AUTO')
                """, [user_email, flight_number])

            messages.success(request, "Klaim berhasil diajukan!")

        except Exception as e:
            messages.error(request, f"Gagal klaim: {str(e)}")

        return redirect('claim_miles')

    claims = ClaimMissingMiles.objects.filter(email_member=user_email).order_by('-timestamp')
    return render(request, 'claim_miles.html', {'claims': claims})

def transfer_miles(request):
    user_email, role = get_user_from_request(request)
    from features.accounts.models import TransferMiles

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
            with connection.cursor() as cursor:
                cursor.execute("SELECT award_miles FROM MEMBER WHERE email=%s", [user_email])
                saldo = cursor.fetchone()

                if not saldo or saldo[0] < jumlah:
                    messages.error(request, "Saldo tidak cukup!")
                    return redirect('transfer_miles')

                cursor.execute("""
                    UPDATE MEMBER
                    SET award_miles = award_miles - %s
                    WHERE email = %s
                """, [jumlah, user_email])

                cursor.execute("""
                    UPDATE MEMBER
                    SET award_miles = award_miles + %s
                    WHERE email = %s
                """, [jumlah, to_email])

                cursor.execute("""
                    INSERT INTO TRANSFER (email_member_1, email_member_2, jumlah, catatan)
                    VALUES (%s, %s, %s, 'Transfer 1')
                """, [user_email, to_email, jumlah])

            messages.success(request, "Transfer berhasil!")

        except Exception as e:
            messages.error(request, f"Gagal transfer: {str(e)}")

        return redirect('transfer_miles')

    transfers = TransferMiles.objects.filter(email_member_1=user_email).order_by('-timestamp')
    return render(request, 'transfer_miles.html', {'transfers': transfers})

def manage_claims(request):
    from features.accounts.models import ClaimMissingMiles

    claims = ClaimMissingMiles.objects.all().order_by('-timestamp')
    status_filter = request.GET.get('status')

    if status_filter:
        claims = claims.filter(status_penerimaan=status_filter)

    return render(request, 'manage_claims.html', {
        'claims': claims,
        'status_filter': status_filter,
    })


def approve_claim(request, id):
    user_email, _ = get_user_from_request(request)

    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE CLAIM_MISSING_MILES
            SET status_penerimaan = 'Disetujui',
                email_staf = %s
            WHERE id = %s
        """, [user_email, id])

    return redirect('manage_claims')


def reject_claim(request, id):
    user_email, _ = get_user_from_request(request)

    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE CLAIM_MISSING_MILES
            SET status_penerimaan = 'Ditolak',
                email_staf = %s
            WHERE id = %s
        """, [user_email, id])

    return redirect('manage_claims')

def transaction_report(request):
    from features.accounts.models import Member, ClaimMissingMiles, TransferMiles, Redeem

    return render(request, 'transaction_report.html', {
        'total_members': Member.objects.count(),
        'total_claims': ClaimMissingMiles.objects.count(),
        'pending_claims': ClaimMissingMiles.objects.filter(status_penerimaan='Menunggu').count(),
        'approved_claims': ClaimMissingMiles.objects.filter(status_penerimaan='Disetujui').count(),
        'rejected_claims': ClaimMissingMiles.objects.filter(status_penerimaan='Ditolak').count(),
        'claims': ClaimMissingMiles.objects.all().order_by('-timestamp'),
        'transfers': TransferMiles.objects.all().order_by('-timestamp'),
        'total_redeems': Redeem.objects.count(),
    })