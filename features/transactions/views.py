from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection


def dict_fetchall(cursor):
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def format_number(value):
    return f"{int(value or 0):,}".replace(",", ".")


def format_rupiah(value):
    return f"Rp {format_number(value)}"


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
    user_email, role = get_user_from_request(request)

    if not user_email:
        return redirect('login')
    if role != 'staf':
        return redirect('dashboard')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                (SELECT COUNT(*) FROM member) AS total_members,
                (SELECT COUNT(*) FROM claim_missing_miles) AS total_claims,
                (SELECT COUNT(*) FROM claim_missing_miles WHERE status_penerimaan = 'Menunggu') AS pending_claims,
                (SELECT COUNT(*) FROM claim_missing_miles WHERE status_penerimaan = 'Disetujui') AS approved_claims,
                (SELECT COUNT(*) FROM claim_missing_miles WHERE status_penerimaan = 'Ditolak') AS rejected_claims,
                (SELECT COUNT(*) FROM transfer) AS total_transfers,
                (SELECT COUNT(*) FROM redeem) AS total_redeems,
                (SELECT COUNT(*) FROM member_award_miles_package) AS total_package_purchases,
                COALESCE((SELECT SUM(jumlah) FROM transfer), 0) AS transfer_miles,
                COALESCE((
                    SELECT SUM(h.miles)
                    FROM redeem r
                    JOIN hadiah h ON h.kode_hadiah = r.kode_hadiah
                ), 0) AS redeem_miles,
                COALESCE((
                    SELECT SUM(amp.jumlah_award_miles)
                    FROM member_award_miles_package map
                    JOIN award_miles_package amp ON amp.id = map.id_award_miles_package
                ), 0) AS package_miles
        """)
        stats = dict_fetchall(cursor)[0]

        cursor.execute("""
            SELECT
                email_member,
                email_staf,
                maskapai,
                bandara_asal,
                bandara_tujuan,
                tanggal_penerbangan,
                flight_number,
                nomor_tiket,
                kelas_kabin,
                pnr,
                status_penerimaan,
                timestamp
            FROM claim_missing_miles
            ORDER BY timestamp DESC
        """)
        claims = dict_fetchall(cursor)

        cursor.execute("""
            SELECT
                email_member_1,
                email_member_2,
                jumlah,
                catatan,
                timestamp
            FROM transfer
            ORDER BY timestamp DESC
        """)
        transfers = dict_fetchall(cursor)

        cursor.execute("""
            SELECT
                r.email_member,
                r.kode_hadiah,
                h.nama AS nama_hadiah,
                h.miles,
                r.timestamp
            FROM redeem r
            JOIN hadiah h ON h.kode_hadiah = r.kode_hadiah
            ORDER BY r.timestamp DESC
        """)
        redeems = dict_fetchall(cursor)

        cursor.execute("""
            SELECT
                map.email_member,
                map.id_award_miles_package AS id_paket,
                amp.jumlah_award_miles,
                amp.harga_paket,
                map.timestamp
            FROM member_award_miles_package map
            JOIN award_miles_package amp ON amp.id = map.id_award_miles_package
            ORDER BY map.timestamp DESC
        """)
        package_purchases = dict_fetchall(cursor)

        cursor.execute("""
            SELECT *
            FROM (
                SELECT
                    'Beli Package' AS jenis,
                    map.email_member AS member_email,
                    NULL AS member_lawan,
                    map.id_award_miles_package AS referensi,
                    amp.jumlah_award_miles AS miles,
                    'Masuk' AS arah,
                    map.timestamp AS timestamp
                FROM member_award_miles_package map
                JOIN award_miles_package amp ON amp.id = map.id_award_miles_package

                UNION ALL

                SELECT
                    'Redeem Hadiah' AS jenis,
                    r.email_member AS member_email,
                    NULL AS member_lawan,
                    r.kode_hadiah AS referensi,
                    h.miles AS miles,
                    'Keluar' AS arah,
                    r.timestamp AS timestamp
                FROM redeem r
                JOIN hadiah h ON h.kode_hadiah = r.kode_hadiah

                UNION ALL

                SELECT
                    'Transfer Keluar' AS jenis,
                    t.email_member_1 AS member_email,
                    t.email_member_2 AS member_lawan,
                    'TRANSFER' AS referensi,
                    t.jumlah AS miles,
                    'Keluar' AS arah,
                    t.timestamp AS timestamp
                FROM transfer t

                UNION ALL

                SELECT
                    'Transfer Masuk' AS jenis,
                    t.email_member_2 AS member_email,
                    t.email_member_1 AS member_lawan,
                    'TRANSFER' AS referensi,
                    t.jumlah AS miles,
                    'Masuk' AS arah,
                    t.timestamp AS timestamp
                FROM transfer t
            ) transaksi
            ORDER BY timestamp DESC
            LIMIT 30
        """)
        latest_transactions = dict_fetchall(cursor)

    for key, value in list(stats.items()):
        if key.startswith('total_') or key.endswith('_claims') or key.endswith('_miles'):
            stats[f'{key}_display'] = format_number(value)

    for transfer in transfers:
        transfer['jumlah_display'] = format_number(transfer['jumlah'])

    for redeem in redeems:
        redeem['miles_display'] = format_number(redeem['miles'])

    for purchase in package_purchases:
        purchase['miles_display'] = format_number(purchase['jumlah_award_miles'])
        purchase['harga_display'] = format_rupiah(purchase['harga_paket'])

    for item in latest_transactions:
        item['miles_display'] = format_number(item['miles'])
        item['signed_miles_display'] = (
            f"+{item['miles_display']}" if item['arah'] == 'Masuk' else f"-{item['miles_display']}"
        )

    return render(request, 'transaction_report.html', {
        'stats': stats,
        'claims': claims,
        'transfers': transfers,
        'redeems': redeems,
        'package_purchases': package_purchases,
        'latest_transactions': latest_transactions,
    })
