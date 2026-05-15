from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import hashlib
from datetime import date, datetime

from main.db import execute_query, execute_write


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def get_user_from_request(request):
    """Get user from session"""
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    return user_email, user_role


def landing(request):
    user_email, role = get_user_from_request(request)
    if user_email:
        return redirect('dashboard')
    return render(request, 'landing.html')


def login_view(request):
    user_email, role = get_user_from_request(request)
    if user_email:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not email or not password:
            messages.error(request, 'Email dan password harus diisi')
            return render(request, 'login.html')

        hashed = hash_password(password)

        user = execute_query(
            "SELECT * FROM pengguna WHERE email = %s AND password = %s",
            (email, hashed),
            fetch_one=True
        )

        if user:
            member = execute_query(
                "SELECT * FROM member WHERE email = %s",
                (email,),
                fetch_one=True
            )
            if member:
                messages.success(request, 'Welcome back!')
                request.session['user_email'] = email
                request.session['user_role'] = 'member'
                return redirect('dashboard')

            staf = execute_query(
                "SELECT * FROM staf WHERE email = %s",
                (email,),
                fetch_one=True
            )
            if staf:
                messages.success(request, 'Welcome back!')
                request.session['user_email'] = email
                request.session['user_role'] = 'staf'
                return redirect('dashboard')

        messages.error(request, 'Email atau password salah')

    return render(request, 'login.html')


def register(request):
    user_email, role = get_user_from_request(request)
    if user_email:
        return redirect('dashboard')

    # Get tiers and airlines for dropdown
    tiers = execute_query("SELECT * FROM tier", fetch_all=True)
    airlines = execute_query("SELECT * FROM maskapai", fetch_all=True)

    selected_role = request.GET.get('role', 'member')
    if request.method == 'POST':
        selected_role = request.POST.get('role', selected_role)

        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        salutation = request.POST.get('salutation', '')
        first_mid_name = request.POST.get('first_mid_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        country_code = request.POST.get('country_code', '').strip()
        mobile_number = request.POST.get('mobile_number', '').strip()
        tanggal_lahir = request.POST.get('tanggal_lahir', '')
        kewarganegaraan = request.POST.get('kewarganegaraan', '').strip()

        errors = []
        if not email:
            errors.append('Email harus diisi')
        if not password1:
            errors.append('Password harus diisi')
        if password1 != password2:
            errors.append('Password dan konfirmasi password tidak cocok')
        if not last_name:
            errors.append('Nama Belakang harus diisi')
        if selected_role == 'staf' and not request.POST.get('airline', ''):
            errors.append('Kode Maskapai wajib dipilih')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'register.html', {
                'tiers': tiers, 'airlines': airlines, 'role': selected_role
            })

        existing = execute_query(
            "SELECT email FROM pengguna WHERE email = %s",
            (email,),
            fetch_one=True
        )
        if existing:
            messages.error(request, 'Email sudah terdaftar')
            return render(request, 'register.html', {
                'tiers': tiers, 'airlines': airlines, 'role': selected_role
            })

        try:
            execute_write(
                """INSERT INTO pengguna (email, password, salutation, first_mid_name, last_name,
                   country_code, mobile_number, tanggal_lahir, kewarganegaraan)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (email, hash_password(password1), salutation, first_mid_name, last_name,
                 country_code, mobile_number, tanggal_lahir or None, kewarganegaraan)
            )

            if selected_role == 'staf':
                airline_code = request.POST.get('airline', '')
                staff_count = execute_query("SELECT COUNT(*) as cnt FROM staf", fetch_one=True)
                staff_num = staff_count['cnt'] + 1

                execute_write(
                    """INSERT INTO staf (email, id_staf, kode_maskapai)
                       VALUES (%s, %s, %s)""",
                    (email, f'SF{date.today().year}{staff_num:04d}', airline_code)
                )
                messages.success(request, 'Selamat datang di AeroMiles!')
                request.session['user_email'] = email
                request.session['user_role'] = 'staf'
            else:
                member_count = execute_query("SELECT COUNT(*) as cnt FROM member", fetch_one=True)
                member_num = member_count['cnt'] + 1

                execute_write(
                    """INSERT INTO member (email, nomor_member, tanggal_bergabung, id_tier, award_miles, total_miles)
                       VALUES (%s, %s, %s, %s, 0, 0)""",
                    (email, f'M{str(date.today().year)}{member_num:04d}', date.today(), 'BASIC')
                )
                messages.success(request, 'Selamat datang di AeroMiles!')
                request.session['user_email'] = email
                request.session['user_role'] = 'member'
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    return render(request, 'register.html', {
        'tiers': tiers, 'airlines': airlines, 'role': selected_role
    })


def logout_view(request):
    request.session.flush()
    messages.success(request, 'Anda telah logout')
    return redirect('login')


def dashboard(request):
    user_email, role = get_user_from_request(request)
    if not user_email:
        return redirect('login')

    pengguna = None
    member_data = None
    staf_data = None
    recent_transactions = []
    staff_claim_summary = {'menunggu': 0, 'disetujui': 0, 'ditolak': 0}

    pengguna = execute_query(
        "SELECT * FROM pengguna WHERE email = %s",
        (user_email,),
        fetch_one=True
    )

    if role == 'member':
        member_data = execute_query(
            "SELECT * FROM member WHERE email = %s",
            (user_email,),
            fetch_one=True
        )

        if member_data:
            claims = execute_query(
                """SELECT id, maskapai, bandara_asal, bandara_tujuan, tanggal_penerbangan,
                   flight_number, status_penerimaan, timestamp
                   FROM claim_missing_miles
                   WHERE email_member = %s
                   ORDER BY timestamp DESC LIMIT 5""",
                (user_email,),
                fetch_all=True
            ) or []

            transfers_sent = execute_query(
                """SELECT email_member_2, jumlah, catatan, timestamp
                   FROM transfer
                   WHERE email_member_1 = %s
                   ORDER BY timestamp DESC LIMIT 5""",
                (user_email,),
                fetch_all=True
            ) or []

            transfers_received = execute_query(
                """SELECT email_member_1, jumlah, catatan, timestamp
                   FROM transfer
                   WHERE email_member_2 = %s
                   ORDER BY timestamp DESC LIMIT 5""",
                (user_email,),
                fetch_all=True
            ) or []

            redeems = execute_query(
                """SELECT kode_hadiah, timestamp
                   FROM redeem
                   WHERE email_member = %s
                   ORDER BY timestamp DESC LIMIT 5""",
                (user_email,),
                fetch_all=True
            ) or []

            package_purchases = execute_query(
                """SELECT id, jumlah_award_miles, timestamp
                   FROM member_award_miles_package
                   WHERE email_member = %s
                   ORDER BY timestamp DESC LIMIT 5""",
                (user_email,),
                fetch_all=True
            ) or []

            for c in claims:
                recent_transactions.append({
                    'type': 'Klaim',
                    'description': f"{c['maskapai']} {c['bandara_asal']}->{c['bandara_tujuan']}",
                    'amount': 0,
                    'status': c['status_penerimaan'],
                    'timestamp': c['timestamp']
                })

            for t in transfers_sent:
                recent_transactions.append({
                    'type': 'Transfer',
                    'description': f"Kirim ke {t['email_member_2']}",
                    'amount': -t['jumlah'],
                    'status': 'Selesai',
                    'timestamp': t['timestamp']
                })

            for t in transfers_received:
                recent_transactions.append({
                    'type': 'Transfer',
                    'description': f"Terima dari {t['email_member_1']}",
                    'amount': t['jumlah'],
                    'status': 'Selesai',
                    'timestamp': t['timestamp']
                })

            for r in redeems:
                recent_transactions.append({
                    'type': 'Redeem',
                    'description': r['kode_hadiah'],
                    'amount': 0,
                    'status': 'Selesai',
                    'timestamp': r['timestamp']
                })

            for p in package_purchases:
                recent_transactions.append({
                    'type': 'Beli Package',
                    'description': p['id'],
                    'amount': p['jumlah_award_miles'],
                    'status': 'Selesai',
                    'timestamp': p['timestamp']
                })

            recent_transactions.sort(key=lambda x: x['timestamp'] if x['timestamp'] else datetime.min, reverse=True)
            recent_transactions = recent_transactions[:5]

    elif role == 'staf':
        staf_data = execute_query(
            "SELECT * FROM staf WHERE email = %s",
            (user_email,),
            fetch_one=True
        )

        if staf_data:
            waiting = execute_query(
                "SELECT COUNT(*) as cnt FROM claim_missing_miles WHERE status_penerimaan = 'Menunggu'",
                fetch_one=True
            )
            staff_claim_summary['menunggu'] = waiting['cnt'] if waiting else 0

            approved = execute_query(
                "SELECT COUNT(*) as cnt FROM claim_missing_miles WHERE email_staf = %s AND status_penerimaan = 'Disetujui'",
                (user_email,),
                fetch_one=True
            )
            staff_claim_summary['disetujui'] = approved['cnt'] if approved else 0

            rejected = execute_query(
                "SELECT COUNT(*) as cnt FROM claim_missing_miles WHERE email_staf = %s AND status_penerimaan = 'Ditolak'",
                (user_email,),
                fetch_one=True
            )
            staff_claim_summary['ditolak'] = rejected['cnt'] if rejected else 0

    return render(request, 'dashboard.html', {
        'user_email': user_email,
        'role': role,
        'member': member_data,
        'staf': staf_data,
        'pengguna': pengguna,
        'recent_transactions': recent_transactions,
        'staff_claim_summary': staff_claim_summary,
    })


def profile(request):
    user_email, role = get_user_from_request(request)
    if not user_email:
        return redirect('login')

    pengguna = execute_query(
        "SELECT * FROM pengguna WHERE email = %s",
        (user_email,),
        fetch_one=True
    )

    if not pengguna:
        return redirect('login')

    member = execute_query(
        "SELECT * FROM member WHERE email = %s",
        (user_email,),
        fetch_one=True
    )

    if request.method == 'POST':
        salutation = request.POST.get('salutation', '')
        first_mid_name = request.POST.get('first_mid_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        country_code = request.POST.get('country_code', '').strip()
        mobile_number = request.POST.get('mobile_number', '').strip()
        tanggal_lahir = request.POST.get('tanggal_lahir', '')
        kewarganegaraan = request.POST.get('kewarganegaraan', '').strip()

        execute_write(
            """UPDATE pengguna SET salutation = %s, first_mid_name = %s, last_name = %s,
               country_code = %s, mobile_number = %s, tanggal_lahir = %s, kewarganegaraan = %s
               WHERE email = %s""",
            (salutation, first_mid_name, last_name, country_code, mobile_number,
             tanggal_lahir or None, kewarganegaraan, user_email)
        )
        messages.success(request, 'Profil berhasil diperbarui')
        return redirect('profile')

    return render(request, 'profile.html', {
        'pengguna': pengguna,
        'member': member,
        'user_email': user_email,
        'role': role,
    })


def change_password(request):
    user_email, role = get_user_from_request(request)

    if request.method == 'POST':
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not old_password or not new_password:
            messages.error(request, 'Password lama dan baru harus diisi')
        elif new_password != confirm_password:
            messages.error(request, 'Password baru dan konfirmasi tidak cocok')
        else:
            pengguna = execute_query(
                "SELECT password FROM pengguna WHERE email = %s",
                (user_email,),
                fetch_one=True
            )

            if pengguna and pengguna['password'] == hash_password(old_password):
                execute_write(
                    "UPDATE pengguna SET password = %s WHERE email = %s",
                    (hash_password(new_password), user_email)
                )
                messages.success(request, 'Password berhasil diubah')
                return redirect('profile')
            else:
                messages.error(request, 'Password lama salah')

    return render(request, 'change_password.html')


# ========== CRUD Identity ==========

def manage_identity(request):
    user_email, role = get_user_from_request(request)
    if not user_email:
        return redirect('login')

    if role != 'member':
        return redirect('dashboard')

    identities = execute_query(
        "SELECT * FROM identitas WHERE email_member = %s",
        (user_email,),
        fetch_all=True
    ) or []

    return render(request, 'manage_identity.html', {
        'identities': identities,
        'user_email': user_email,
    })


def create_identity(request):
    user_email, role = get_user_from_request(request)

    if request.method == 'POST':
        nomor = request.POST.get('nomor', '').strip()
        jenis = request.POST.get('jenis', '')
        negara_penerbit = request.POST.get('negara_penerbit', '').strip()
        tanggal_terbit = request.POST.get('tanggal_terbit', '')
        tanggal_habis = request.POST.get('tanggal_habis', '')

        if not nomor or not jenis:
            messages.error(request, 'Nomor dokumen dan jenis wajib diisi')
        else:
            existing = execute_query(
                "SELECT nomor FROM identitas WHERE nomor = %s",
                (nomor,),
                fetch_one=True
            )
            if existing:
                messages.error(request, 'Nomor dokumen sudah terdaftar')
            else:
                try:
                    execute_write(
                        """INSERT INTO identitas (nomor, email_member, jenis, negara_penerbit, tanggal_terbit, tanggal_habis)
                           VALUES (%s, %s, %s, %s, %s, %s)""",
                        (nomor, user_email, jenis, negara_penerbit, tanggal_terbit or None, tanggal_habis or None)
                    )
                    messages.success(request, 'Identitas berhasil ditambahkan')
                except Exception as e:
                    messages.error(request, f'Error: {str(e)}')

        return redirect('identity')

    return render(request, 'create_identity.html', {'user_email': user_email})


def edit_identity(request, identity_id):
    identity = execute_query(
        "SELECT * FROM identitas WHERE nomor = %s",
        (identity_id,),
        fetch_one=True
    )

    user_email, role = get_user_from_request(request)

    if request.method == 'GET':
        if not identity:
            return JsonResponse({'error': 'Not found'}, status=404)
        return JsonResponse({
            'identity': {
                'nomor': identity['nomor'],
                'jenis': identity['jenis'],
                'negara_penerbit': identity['negara_penerbit'],
                'tanggal_terbit': str(identity['tanggal_terbit']) if identity['tanggal_terbit'] else '',
                'tanggal_habis': str(identity['tanggal_habis']) if identity['tanggal_habis'] else '',
            }
        })

    if request.method == 'POST':
        if user_email != identity['email_member']:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        jenis = request.POST.get('jenis', '')
        negara_penerbit = request.POST.get('negara_penerbit', '').strip()
        tanggal_terbit = request.POST.get('tanggal_terbit', '')
        tanggal_habis = request.POST.get('tanggal_habis', '')

        try:
            execute_write(
                """UPDATE identitas SET jenis = %s, negara_penerbit = %s, tanggal_terbit = %s, tanggal_habis = %s
                   WHERE nomor = %s""",
                (jenis, negara_penerbit, tanggal_terbit or None, tanggal_habis or None, identity_id)
            )
            return JsonResponse({'success': True, 'message': 'Identitas berhasil diperbarui'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid'}, status=405)


@require_POST
def delete_identity(request, identity_id):
    user_email, role = get_user_from_request(request)

    identity = execute_query(
        "SELECT email_member FROM identitas WHERE nomor = %s",
        (identity_id,),
        fetch_one=True
    )

    if identity and user_email == identity['email_member']:
        execute_write("DELETE FROM identitas WHERE nomor = %s", (identity_id,))
        messages.success(request, 'Identitas berhasil dihapus')

    return redirect('identity')


# ========== CRUD Member (Staf) ==========

def manage_members(request):
    user_email, role = get_user_from_request(request)

    tiers = execute_query("SELECT * FROM tier", fetch_all=True) or []
    search = request.GET.get('search', '').strip()
    tier_filter = request.GET.get('tier', '')

    members = execute_query(
        """SELECT m.email, m.nomor_member, m.tanggal_bergabung, m.id_tier,
                  m.award_miles, m.total_miles,
                  p.salutation, p.first_mid_name, p.last_name
           FROM member m
           JOIN pengguna p ON m.email = p.email
           WHERE 1=1
           ORDER BY m.nomor_member""",
        fetch_all=True
    ) or []

    if search:
        members = [m for m in members if
                   search.lower() in (m['email'] or '').lower() or
                   search.lower() in (m['first_mid_name'] or '').lower() or
                   search.lower() in (m['last_name'] or '').lower() or
                   search.lower() in (m['nomor_member'] or '').lower()]

    if tier_filter:
        members = [m for m in members if m['id_tier'] == tier_filter]

    return render(request, 'manage_members.html', {
        'members': members,
        'tiers': tiers,
        'search': search,
        'tier_filter': tier_filter,
    })


def create_member(request):
    user_email, role = get_user_from_request(request)

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        salutation = request.POST.get('salutation', '')
        first_mid_name = request.POST.get('first_mid_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        country_code = request.POST.get('country_code', '').strip()
        mobile_number = request.POST.get('phone', '').strip()
        nationality = request.POST.get('nationality', '').strip()
        birth_date = request.POST.get('birth_date', '')

        if not email or not password or not last_name:
            return JsonResponse({'error': 'Email, password, dan last name wajib diisi'}, status=400)

        existing = execute_query(
            "SELECT email FROM pengguna WHERE email = %s",
            (email,),
            fetch_one=True
        )
        if existing:
            return JsonResponse({'error': 'Email sudah terdaftar'}, status=400)

        try:
            execute_write(
                """INSERT INTO pengguna (email, password, salutation, first_mid_name, last_name,
                   country_code, mobile_number, tanggal_lahir, kewarganegaraan)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (email, hash_password(password), salutation, first_mid_name, last_name,
                 country_code, mobile_number, birth_date or None, nationality)
            )

            member_count = execute_query("SELECT COUNT(*) as cnt FROM member", fetch_one=True)
            member_num = member_count['cnt'] + 1

            execute_write(
                """INSERT INTO member (email, nomor_member, tanggal_bergabung, id_tier, award_miles, total_miles)
                   VALUES (%s, %s, %s, %s, 0, 0)""",
                (email, f'M{str(date.today().year)}{member_num:04d}', date.today(), 'BASIC')
            )

            return JsonResponse({'success': True, 'message': f'Member {email} berhasil dibuat'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid'}, status=405)


def edit_member(request, member_id):
    user_email, role = get_user_from_request(request)

    member = execute_query(
        "SELECT * FROM member WHERE email = %s",
        (member_id,),
        fetch_one=True
    )

    if request.method == 'GET':
        if not member:
            return JsonResponse({'error': 'Member not found'}, status=404)
        return JsonResponse({
            'member': {
                'email': member['email'],
                'nomor_member': member['nomor_member'],
                'id_tier': member['id_tier'],
            }
        })

    if request.method == 'POST':
        tier = request.POST.get('tier', 'BASIC')

        try:
            execute_write(
                "UPDATE member SET id_tier = %s WHERE email = %s",
                (tier, member_id)
            )
            return JsonResponse({'success': True, 'message': 'Member berhasil diperbarui'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid'}, status=405)


@require_POST
def delete_member(request, member_id):
    member_id = str(member_id)
    user_email, role = get_user_from_request(request)

    try:
        execute_write("DELETE FROM identitas WHERE email_member = %s", (member_id,))
        execute_write("DELETE FROM claim_missing_miles WHERE email_member = %s", (member_id,))
        execute_write("DELETE FROM transfer WHERE email_member_1 = %s", (member_id,))
        execute_write("DELETE FROM transfer WHERE email_member_2 = %s", (member_id,))
        execute_write("DELETE FROM redeem WHERE email_member = %s", (member_id,))
        execute_write("DELETE FROM member WHERE email = %s", (member_id,))
        execute_write("DELETE FROM pengguna WHERE email = %s", (member_id,))

        messages.success(request, 'Member berhasil dihapus')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')

    return redirect('manage_members')


# ─────────────────────────────────────────────
#  FITUR 16: CRUD MANAJEMEN MITRA (Staf)
# ─────────────────────────────────────────────

def manage_partners(request):
    user_email, role = get_user_from_request(request)
    if role != 'staf':
        return redirect('dashboard')

    search = request.GET.get('search', '').strip()

    mitra_list = execute_query(
        """SELECT email_mitra, id_penyedia, nama_mitra, tanggal_kerja_sama
           FROM mitra ORDER BY nama_mitra""",
        fetch_all=True
    ) or []

    return render(request, 'manage_partners.html', {
        'mitra_list': mitra_list,
        'search': search,
    })


def partner_detail(request, email):
    mitra = execute_query(
        "SELECT * FROM mitra WHERE email_mitra = %s",
        (email,),
        fetch_one=True
    )

    if not mitra:
        return JsonResponse({'error': 'Mitra tidak ditemukan'}, status=404)

    return JsonResponse({'mitra': {
        'email_mitra': mitra['email_mitra'],
        'id_penyedia': mitra['id_penyedia'],
        'nama_mitra': mitra['nama_mitra'],
        'tanggal_kerja_sama': str(mitra['tanggal_kerja_sama']),
    }})


@require_POST
def create_partner(request):
    user_email, role = get_user_from_request(request)
    if role != 'staf':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    email_mitra = request.POST.get('email_mitra', '').strip()
    nama_mitra = request.POST.get('nama_mitra', '').strip()
    tanggal = request.POST.get('tanggal_kerja_sama', '').strip()

    if not all([email_mitra, nama_mitra, tanggal]):
        return JsonResponse({'error': 'Semua field wajib harus diisi'})

    existing = execute_query(
        "SELECT email_mitra FROM mitra WHERE email_mitra = %s",
        (email_mitra,),
        fetch_one=True
    )
    if existing:
        return JsonResponse({'error': 'Email mitra sudah terdaftar'})

    try:
        new_id_result = execute_query("SELECT COALESCE(MAX(id), 0) + 1 as new_id FROM penyedia", fetch_one=True)
        new_id = new_id_result['new_id']

        execute_write("INSERT INTO penyedia (id) VALUES (%s)", (new_id,))
        execute_write(
            "INSERT INTO mitra (email_mitra, id_penyedia, nama_mitra, tanggal_kerja_sama) VALUES (%s, %s, %s, %s)",
            (email_mitra, new_id, nama_mitra, tanggal)
        )
        return JsonResponse({'success': True, 'message': f'Mitra {nama_mitra} berhasil ditambahkan (ID Penyedia: {new_id})'})
    except Exception as e:
        return JsonResponse({'error': str(e)})


@require_POST
def edit_partner(request, email):
    user_email, role = get_user_from_request(request)
    if role != 'staf':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    nama_mitra = request.POST.get('nama_mitra', '').strip()
    tanggal = request.POST.get('tanggal_kerja_sama', '').strip()

    if not all([nama_mitra, tanggal]):
        return JsonResponse({'error': 'Semua field wajib harus diisi'})

    try:
        execute_write(
            "UPDATE mitra SET nama_mitra = %s, tanggal_kerja_sama = %s WHERE email_mitra = %s",
            (nama_mitra, tanggal, email)
        )
        return JsonResponse({'success': True, 'message': 'Mitra berhasil diperbarui'})
    except Exception as e:
        return JsonResponse({'error': str(e)})


@require_POST
def delete_partner(request, email):
    _, role = get_user_from_request(request)
    if role != 'staf':
        return redirect('dashboard')

    mitra = execute_query(
        "SELECT id_penyedia FROM mitra WHERE email_mitra = %s",
        (email,),
        fetch_one=True
    )

    if mitra:
        pid = mitra['id_penyedia']
        try:
            execute_write("DELETE FROM mitra WHERE email_mitra = %s", (email,))
            execute_write("DELETE FROM penyedia WHERE id = %s", (pid,))
            messages.success(request, 'Mitra berhasil dihapus.')
        except Exception as e:
            messages.error(request, str(e))
    else:
        messages.error(request, 'Mitra tidak ditemukan.')

    return redirect('manage_partners')