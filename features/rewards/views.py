from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection, transaction
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from datetime import date


def dict_fetchall(cursor):
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def dict_fetchone(cursor):
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [column[0] for column in cursor.description]
    return dict(zip(columns, row))


def format_number(value):
    return f"{int(value or 0):,}".replace(",", ".")


def format_rupiah(value):
    return f"Rp {format_number(value)}"


def dict_fetchall(cursor):
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def format_number(value):
    return f"{int(value or 0):,}".replace(",", ".")


def format_rupiah(value):
    return f"Rp {format_number(value)}"


def get_user_from_request(request):
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    return user_email, user_role


# =============================================================================
#  REDEEM HADIAH (Member)
# =============================================================================

def redeem_rewards(request):
    """Redeem Hadiah - untuk Member"""
    user_email, role = get_user_from_request(request)

    if not user_email:
        return redirect('login')
    if role != 'member':
        return redirect('dashboard')

    if request.method == 'POST':
        kode_hadiah = request.POST.get('kode_hadiah', '').strip()

        if not kode_hadiah:
            messages.error(request, 'Hadiah wajib dipilih.')
            return redirect('redeem_rewards')

        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE MEMBER
                        SET award_miles = award_miles - h.miles
                        FROM HADIAH h
                        WHERE MEMBER.email = %s
                            AND h.kode_hadiah = %s
                            AND MEMBER.award_miles >= h.miles
                            AND CURRENT_DATE >= h.valid_start_date
                            AND CURRENT_DATE <= h.program_end
                        RETURNING h.kode_hadiah, h.nama
                    """, [user_email, kode_hadiah])
                    redeemed = cursor.fetchone()

                    if not redeemed:
                        messages.error(request, 'Hadiah tidak valid atau award miles tidak mencukupi.')
                        return redirect('redeem_rewards')

                    reward_code, reward_name = redeemed

                    cursor.execute("""
                        INSERT INTO REDEEM (
                            email_member,
                            kode_hadiah,
                            timestamp
                        )
                        VALUES (
                            %s,
                            %s,
                            CURRENT_TIMESTAMP
                        )
                    """, [user_email, reward_code])

            messages.success(request, f'Redeem {reward_name} berhasil.')
            return redirect(f"{reverse('redeem_rewards')}?tab=history")
        except Exception as e:
            messages.error(request, f'Gagal redeem hadiah: {str(e)}')
            return redirect('redeem_rewards')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT award_miles
            FROM member
            WHERE email = %s
        """, [user_email])
        member_row = cursor.fetchone()

        if not member_row:
            messages.error(request, 'Akun member tidak ditemukan.')
            return redirect('dashboard')

        member = {
            'email': user_email,
            'award_miles': member_row[0] or 0,
            'award_miles_display': format_number(member_row[0] or 0),
        }

        cursor.execute("""
            SELECT
                h.kode_hadiah,
                h.nama AS nama_hadiah,
                m.nama_maskapai AS penyedia,
                h.miles AS jumlah_miles_dibutuhkan,
                h.deskripsi,
                h.valid_start_date,
                h.program_end
            FROM HADIAH h
            JOIN MASKAPAI m
                ON h.id_penyedia = m.id_penyedia
            WHERE h.program_end >= CURRENT_DATE

            UNION

            SELECT
                h.kode_hadiah,
                h.nama AS nama_hadiah,
                ma.nama_mitra AS penyedia,
                h.miles AS jumlah_miles_dibutuhkan,
                h.deskripsi,
                h.valid_start_date,
                h.program_end
            FROM HADIAH h
            JOIN MITRA ma
                ON h.id_penyedia = ma.id_penyedia
            WHERE h.program_end >= CURRENT_DATE
        """)
        rewards = dict_fetchall(cursor)

        cursor.execute("""
            SELECT
                r.kode_hadiah,
                h.nama,
                h.miles,
                r.timestamp
            FROM redeem r
            JOIN hadiah h ON h.kode_hadiah = r.kode_hadiah
            WHERE r.email_member = %s
            ORDER BY r.timestamp DESC
        """, [user_email])
        redeem_history = dict_fetchall(cursor)

    for reward in rewards:
        reward['miles_display'] = format_number(reward['jumlah_miles_dibutuhkan'])
    for item in redeem_history:
        item['miles_display'] = format_number(item['miles'])

    active_tab = request.GET.get('tab', 'catalog')
    if active_tab not in ('catalog', 'history'):
        active_tab = 'catalog'

    return render(request, 'redeem_rewards.html', {
        'member': member,
        'rewards': rewards,
        'redeem_history': redeem_history,
        'active_tab': active_tab,
    })

        if not kode_hadiah:
            messages.error(request, 'Hadiah wajib dipilih.')
            return redirect('redeem_rewards')

        try:
            with connection.cursor() as cursor:
                # Trigger BEFORE INSERT akan validasi saldo & periode
                # Trigger AFTER INSERT akan potong award_miles otomatis
                cursor.execute("""
                    INSERT INTO REDEEM (email_member, kode_hadiah, timestamp)
                    VALUES (%s, %s, CURRENT_TIMESTAMP)
                """, [user_email, kode_hadiah])

            messages.success(request, 'Redeem hadiah berhasil.')
            return redirect(f"{reverse('redeem_rewards')}?tab=history")

        except Exception as e:
            error_msg = str(e)
            if 'ERROR:' in error_msg:
                error_msg = error_msg.split('ERROR:')[-1].strip().split('\n')[0]
            messages.error(request, error_msg)
            return redirect('redeem_rewards')

    with connection.cursor() as cursor:
        # Data member
        cursor.execute("""
            SELECT award_miles
            FROM member
            WHERE email = %s
        """, [user_email])
        member_row = cursor.fetchone()

        if not member_row:
            messages.error(request, 'Akun member tidak ditemukan.')
            return redirect('dashboard')

        member = {
            'email': user_email,
            'award_miles': member_row[0] or 0,
            'award_miles_display': format_number(member_row[0] or 0),
        }

        # Daftar hadiah aktif dari maskapai UNION mitra
        cursor.execute("""
            SELECT
                h.kode_hadiah,
                h.nama AS nama_hadiah,
                m.nama_maskapai AS penyedia,
                h.miles AS jumlah_miles_dibutuhkan,
                h.deskripsi,
                h.valid_start_date,
                h.program_end
            FROM hadiah h
            JOIN maskapai m ON h.id_penyedia = m.id_penyedia
            WHERE h.program_end >= CURRENT_DATE

            UNION

            SELECT
                h.kode_hadiah,
                h.nama AS nama_hadiah,
                ma.nama_mitra AS penyedia,
                h.miles AS jumlah_miles_dibutuhkan,
                h.deskripsi,
                h.valid_start_date,
                h.program_end
            FROM hadiah h
            JOIN mitra ma ON h.id_penyedia = ma.id_penyedia
            WHERE h.program_end >= CURRENT_DATE

            ORDER BY kode_hadiah
        """)
        rewards = dict_fetchall(cursor)

        # Riwayat redeem member
        cursor.execute("""
            SELECT
                r.kode_hadiah,
                h.nama,
                h.miles,
                r.timestamp
            FROM redeem r
            JOIN hadiah h ON h.kode_hadiah = r.kode_hadiah
            WHERE r.email_member = %s
            ORDER BY r.timestamp DESC
        """, [user_email])
        redeem_history = dict_fetchall(cursor)

    for reward in rewards:
        reward['miles_display'] = format_number(reward['jumlah_miles_dibutuhkan'])
    for item in redeem_history:
        item['miles_display'] = format_number(item['miles'])

    active_tab = request.GET.get('tab', 'catalog')
    if active_tab not in ('catalog', 'history'):
        active_tab = 'catalog'

    return render(request, 'redeem_rewards.html', {
        'member': member,
        'rewards': rewards,
        'redeem_history': redeem_history,
        'active_tab': active_tab,
    })


# =============================================================================
#  BELI PACKAGE (Member)
# =============================================================================

def buy_packages(request):
    """Beli Package - untuk Member"""
    user_email, role = get_user_from_request(request)

    if not user_email:
        return redirect('login')
    if role != 'member':
        return redirect('dashboard')

    if request.method == 'POST':
        package_id = request.POST.get('package_id', '').strip()

        if not package_id:
            messages.error(request, 'Package wajib dipilih.')
            return redirect('buy_packages')

        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE MEMBER
                        SET award_miles = award_miles + amp.jumlah_award_miles
                        FROM AWARD_MILES_PACKAGE amp
                        WHERE MEMBER.email = %s
                          AND amp.id = %s
                        RETURNING amp.id, amp.jumlah_award_miles
                    """, [user_email, package_id])
                    package = cursor.fetchone()

                    if not package:
                        messages.error(request, 'Package atau akun member tidak ditemukan.')
                        return redirect('buy_packages')

                    selected_id, package_miles = package

                    cursor.execute("""
                        INSERT INTO MEMBER_AWARD_MILES_PACKAGE (
                            id_award_miles_package,
                            email_member,
                            timestamp
                        )
                        VALUES (
                            %s,
                            %s,
                            CURRENT_TIMESTAMP
                        )
                    """, [selected_id, user_email])

            messages.success(
                request,
                f'Pembelian package {selected_id} berhasil. Award miles bertambah {format_number(package_miles)}.'
            )
            return redirect('buy_packages')
        except Exception as e:
            messages.error(request, f'Gagal membeli package: {str(e)}')
            return redirect('buy_packages')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT award_miles
            FROM member
            WHERE email = %s
        """, [user_email])
        member_row = cursor.fetchone()

        if not member_row:
            messages.error(request, 'Akun member tidak ditemukan.')
            return redirect('dashboard')

        member = {
            'email': user_email,
            'award_miles': member_row[0] or 0,
            'award_miles_display': format_number(member_row[0] or 0),
        }

        cursor.execute("""
            SELECT
                id AS id_paket,
                jumlah_award_miles,
                harga_paket
            FROM AWARD_MILES_PACKAGE
        """)
        packages = dict_fetchall(cursor)

    for package in packages:
        package['harga_display'] = format_rupiah(package['harga_paket'])
        package['miles_display'] = format_number(package['jumlah_award_miles'])

    return render(request, 'buy_packages.html', {
        'member': member,
        'packages': packages,
    })


# =============================================================================
#  TIER INFO (Member)
# =============================================================================

def tier_info(request):
    """Info Tier - untuk Member"""
    user_email, role = get_user_from_request(request)

    if not user_email:
        return redirect('login')
    if role != 'member':
        return redirect('dashboard')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                id_tier,
                nama AS nama_tier,
                minimal_frekuensi_terbang,
                minimal_tier_miles
            FROM tier
            ORDER BY minimal_tier_miles
        """)
        tiers = dict_fetchall(cursor)

        cursor.execute("""
            SELECT
                t.id_tier,
                t.nama AS nama_tier,
                t.minimal_frekuensi_terbang,
                t.minimal_tier_miles
            FROM member m
            JOIN tier t
                ON m.id_tier = t.id_tier
            WHERE m.email = %s
        """, [user_email])
        current_tier = dict_fetchall(cursor)

        if not current_tier:
            messages.error(request, 'Akun member tidak ditemukan.')
            return redirect('dashboard')

        current_tier = current_tier[0]

        cursor.execute("""
            SELECT
                m.total_miles,
                t.nama AS nama_tier_berikutnya,
                t.minimal_tier_miles,
                t.minimal_tier_miles - m.total_miles AS miles_dibutuhkan
            FROM member m
            JOIN tier t
                ON t.minimal_tier_miles > m.total_miles
            WHERE m.email = %s
            ORDER BY t.minimal_tier_miles
            LIMIT 1
        """, [user_email])
        next_tier_rows = dict_fetchall(cursor)

        cursor.execute("""
            SELECT
                email,
                COALESCE(total_miles, 0) AS total_miles
            FROM member
            WHERE email = %s
        """, [user_email])
        member_row = cursor.fetchone()

    total_miles = member_row[1] if member_row else 0
    member = {
        'email': user_email,
        'total_miles': total_miles,
        'total_miles_display': format_number(total_miles),
    }

    next_tier = next_tier_rows[0] if next_tier_rows else None

    for tier in tiers:
        tier['is_current'] = tier['id_tier'] == current_tier['id_tier']
        tier['minimal_frekuensi_terbang_display'] = format_number(tier['minimal_frekuensi_terbang'])
        tier['minimal_tier_miles_display'] = format_number(tier['minimal_tier_miles'])

    progress = {
        'has_next': next_tier is not None,
        'percent': 100,
        'miles_to_next': 0,
        'miles_to_next_display': '0',
    }

    if next_tier:
        next_required = next_tier['minimal_tier_miles']
        miles_to_next = max(next_tier['miles_dibutuhkan'], 0)
        next_tier['minimal_tier_miles_display'] = format_number(next_required)
        progress['percent'] = min(100, int((total_miles / next_required) * 100)) if next_required else 100
        progress['miles_to_next'] = miles_to_next
        progress['miles_to_next_display'] = format_number(miles_to_next)

    return render(request, 'tier_info.html', {
        'member': member,
        'current_tier': current_tier,
        'tiers': tiers,
        'next_tier': next_tier,
        'progress': progress,
    })


# =============================================================================
#  MANAGE REWARDS — HADIAH & PENYEDIA (Staf)
# =============================================================================

def manage_rewards(request):
    """Kelola Hadiah & Penyedia - untuk Staf"""
    user_email, role = get_user_from_request(request)
    if role != 'staf':
        return redirect('dashboard')

    search = request.GET.get('search', '').strip()
    penyedia_filter = request.GET.get('penyedia', '')
    status_filter = request.GET.get('status', '')

    today = date.today()

    with connection.cursor() as cursor:
        # Semua hadiah beserta nama penyedia (maskapai atau mitra)
        cursor.execute("""
            SELECT
                h.kode_hadiah,
                h.nama,
                h.miles,
                h.deskripsi,
                h.valid_start_date,
                h.program_end,
                h.id_penyedia,
                COALESCE(m.nama_maskapai, mt.nama_mitra, 'Penyedia ' || h.id_penyedia::text) AS nama_penyedia,
                CASE
                    WHEN m.id_penyedia IS NOT NULL THEN 'airline'
                    ELSE 'partner'
                END AS tipe_penyedia,
                CASE
                    WHEN h.program_end < CURRENT_DATE THEN true
                    ELSE false
                END AS is_expired
            FROM hadiah h
            LEFT JOIN maskapai m ON h.id_penyedia = m.id_penyedia
            LEFT JOIN mitra mt ON h.id_penyedia = mt.id_penyedia
            ORDER BY h.kode_hadiah
        """)
        all_hadiah = dict_fetchall(cursor)

        # Statistik (unfiltered)
        total_count = len(all_hadiah)
        active_count = sum(1 for h in all_hadiah if not h['is_expired'])
        expired_count = sum(1 for h in all_hadiah if h['is_expired'])

        # Apply filters
        hadiah_list = all_hadiah
        if search:
            hadiah_list = [h for h in hadiah_list if search.lower() in h['nama'].lower()]
        if penyedia_filter:
            hadiah_list = [h for h in hadiah_list if h['tipe_penyedia'] == penyedia_filter]
        if status_filter == 'active':
            hadiah_list = [h for h in hadiah_list if not h['is_expired']]
        elif status_filter == 'expired':
            hadiah_list = [h for h in hadiah_list if h['is_expired']]

        # Dropdown penyedia untuk form
        cursor.execute("""
            SELECT id_penyedia AS id, nama_maskapai AS nama, 'airline' AS tipe
            FROM maskapai

            UNION ALL

            SELECT id_penyedia AS id, nama_mitra AS nama, 'partner' AS tipe
            FROM mitra

            ORDER BY tipe, nama
        """)
        penyedia_list = dict_fetchall(cursor)

    return render(request, 'manage_rewards.html', {
        'hadiah_list': hadiah_list,
        'penyedia_list': penyedia_list,
        'search': search,
        'penyedia_filter': penyedia_filter,
        'status_filter': status_filter,
        'total_count': total_count,
        'active_count': active_count,
        'expired_count': expired_count,
    })


def hadiah_next_kode(request):
    """Return kode hadiah berikutnya untuk ditampilkan di form"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT kode_hadiah
            FROM hadiah
            ORDER BY kode_hadiah DESC
            LIMIT 1
        """)
        row = cursor.fetchone()

    if row:
        try:
            num = int(row[0].split('-')[1]) + 1
        except (IndexError, ValueError):
            num = 1
    else:
        num = 1

    return JsonResponse({'kode': f'RWD-{num:03d}'})


def hadiah_detail(request, kode):
    """Return detail hadiah sebagai JSON untuk edit modal"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT kode_hadiah, nama, miles, deskripsi, valid_start_date, program_end, id_penyedia
            FROM hadiah
            WHERE kode_hadiah = %s
        """, [kode])
        row = dict_fetchone(cursor)

    if not row:
        return JsonResponse({'error': 'Hadiah tidak ditemukan'}, status=404)

    return JsonResponse({'hadiah': {
        'kode_hadiah': row['kode_hadiah'],
        'nama': row['nama'],
        'miles': row['miles'],
        'deskripsi': row['deskripsi'] or '',
        'valid_start_date': str(row['valid_start_date']),
        'program_end': str(row['program_end']),
        'id_penyedia': row['id_penyedia'],
    }})


@require_POST
def create_hadiah(request):
    """Buat hadiah baru"""
    user_email, role = get_user_from_request(request)
    if role != 'staf':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    nama = request.POST.get('nama', '').strip()
    id_penyedia = request.POST.get('id_penyedia', '').strip()
    miles = request.POST.get('miles', '').strip()
    deskripsi = request.POST.get('deskripsi', '').strip()
    valid_start = request.POST.get('valid_start_date', '').strip()
    program_end = request.POST.get('program_end', '').strip()

    if not all([nama, id_penyedia, miles, valid_start, program_end]):
        return JsonResponse({'error': 'Semua field wajib harus diisi'})

    try:
        miles = int(miles)
        id_penyedia = int(id_penyedia)
    except ValueError:
        return JsonResponse({'error': 'Miles dan ID Penyedia harus berupa angka'})

    # Generate kode hadiah
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT kode_hadiah
            FROM hadiah
            ORDER BY kode_hadiah DESC
            LIMIT 1
        """)
        row = cursor.fetchone()

    try:
        num = int(row[0].split('-')[1]) + 1 if row else 1
    except (IndexError, ValueError, TypeError):
        num = 1
    kode = f'RWD-{num:03d}'

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO hadiah (kode_hadiah, nama, miles, deskripsi, valid_start_date, program_end, id_penyedia)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [kode, nama, miles, deskripsi, valid_start, program_end, id_penyedia])
        return JsonResponse({'success': True, 'message': f'Hadiah {kode} berhasil ditambahkan'})
    except Exception as e:
        return JsonResponse({'error': str(e)})


@require_POST
def edit_hadiah(request, kode):
    """Update hadiah"""
    user_email, role = get_user_from_request(request)
    if role != 'staf':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    nama = request.POST.get('nama', '').strip()
    id_penyedia = request.POST.get('id_penyedia', '').strip()
    miles = request.POST.get('miles', '').strip()
    deskripsi = request.POST.get('deskripsi', '').strip()
    valid_start = request.POST.get('valid_start_date', '').strip()
    program_end = request.POST.get('program_end', '').strip()

    if not all([nama, id_penyedia, miles, valid_start, program_end]):
        return JsonResponse({'error': 'Semua field wajib harus diisi'})

    try:
        miles = int(miles)
        id_penyedia = int(id_penyedia)
    except ValueError:
        return JsonResponse({'error': 'Miles dan ID Penyedia harus berupa angka'})

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE hadiah
                SET nama = %s,
                    miles = %s,
                    deskripsi = %s,
                    valid_start_date = %s,
                    program_end = %s,
                    id_penyedia = %s
                WHERE kode_hadiah = %s
            """, [nama, miles, deskripsi, valid_start, program_end, id_penyedia, kode])
        return JsonResponse({'success': True, 'message': 'Hadiah berhasil diperbarui'})
    except Exception as e:
        return JsonResponse({'error': str(e)})


@require_POST
def delete_hadiah(request, kode):
    """Hapus hadiah (hanya yang sudah kadaluarsa)"""
    user_email, role = get_user_from_request(request)

    try:
        with connection.cursor() as cursor:
            # Cek apakah hadiah ada dan belum expired
            cursor.execute("""
                SELECT program_end
                FROM hadiah
                WHERE kode_hadiah = %s
            """, [kode])
            row = cursor.fetchone()

            if not row:
                messages.error(request, 'Hadiah tidak ditemukan.')
                return redirect('manage_rewards')

            program_end = row[0]
            if program_end >= date.today():
                messages.error(request, 'Hanya hadiah yang sudah kadaluarsa yang dapat dihapus.')
                return redirect('manage_rewards')

            cursor.execute("DELETE FROM hadiah WHERE kode_hadiah = %s", [kode])

        messages.success(request, f'Hadiah {kode} berhasil dihapus.')
    except Exception as e:
        messages.error(request, str(e))

    return redirect('manage_rewards')
