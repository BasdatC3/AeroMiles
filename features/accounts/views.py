from django.shortcuts import render, redirect
from django.contrib import messages
import hashlib
from django.db import connection


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def get_user_from_request(request):
    """Get user from session"""
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    return user_email, user_role


def dict_fetchall(cursor):
    """Return all rows from a cursor as a list of dicts"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def dict_fetchone(cursor):
    """Return one row from a cursor as a dict"""
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))


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
        try:
            with connection.cursor() as cursor:
                # Cek pengguna ada dan password cocok
                cursor.execute("""
                    SELECT email FROM pengguna
                    WHERE email = %s AND password = %s
                """, [email, hashed])
                pengguna = cursor.fetchone()

                if not pengguna:
                    messages.error(request, 'Email atau password salah')
                    return render(request, 'login.html')

                # Cek apakah member
                cursor.execute("SELECT email FROM member WHERE email = %s", [email])
                if cursor.fetchone():
                    messages.success(request, 'Welcome back!')
                    request.session['user_email'] = email
                    request.session['user_role'] = 'member'
                    return redirect('dashboard')

                # Cek apakah staf
                cursor.execute("SELECT email FROM staf WHERE email = %s", [email])
                if cursor.fetchone():
                    messages.success(request, 'Welcome back!')
                    request.session['user_email'] = email
                    request.session['user_role'] = 'staf'
                    return redirect('dashboard')

                messages.error(request, 'Email atau password salah')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    return render(request, 'login.html')


def register(request):
    user_email, role = get_user_from_request(request)
    if user_email:
        return redirect('dashboard')

    with connection.cursor() as cursor:
        cursor.execute("SELECT id_tier, nama FROM tier ORDER BY minimal_tier_miles")
        tiers = dict_fetchall(cursor)
        cursor.execute("SELECT kode_maskapai, nama_maskapai FROM maskapai ORDER BY nama_maskapai")
        airlines = dict_fetchall(cursor)

    selected_role = request.GET.get('role', 'member')
    if request.method == 'POST':
        selected_role = request.POST.get('role', selected_role)

    if request.method == 'POST':
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

        try:
            with connection.cursor() as cursor:
                # Cek email sudah ada
                cursor.execute("SELECT email FROM pengguna WHERE LOWER(email) = LOWER(%s)", [email])
                if cursor.fetchone():
                    messages.error(request, 'Email sudah terdaftar')
                    return render(request, 'register.html', {
                        'tiers': tiers, 'airlines': airlines, 'role': selected_role
                    })

                from datetime import date
                # Insert pengguna
                cursor.execute("""
                    INSERT INTO pengguna (email, password, salutation, first_mid_name, last_name,
                        country_code, mobile_number, tanggal_lahir, kewarganegaraan)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    email, hash_password(password1), salutation, first_mid_name, last_name,
                    country_code, mobile_number, tanggal_lahir or None, kewarganegaraan
                ])

                if selected_role == 'staf':
                    airline_code = request.POST.get('airline', '')
                    cursor.execute("SELECT COUNT(*) FROM staf")
                    staff_count = cursor.fetchone()[0] + 1
                    cursor.execute("""
                        INSERT INTO staf (email, id_staf, kode_maskapai)
                        VALUES (%s, %s, %s)
                    """, [email, f'SF{date.today().year}{staff_count:04d}', airline_code])
                    request.session['user_email'] = email
                    request.session['user_role'] = 'staf'
                else:
                    cursor.execute("SELECT COUNT(*) FROM member")
                    member_count = cursor.fetchone()[0] + 1
                    cursor.execute("""
                        INSERT INTO member (email, nomor_member, tanggal_bergabung, id_tier, award_miles, total_miles)
                        VALUES (%s, %s, %s, 'T01', 0, 0)
                    """, [email, f'M{date.today().year}{member_count:04d}', date.today()])
                    request.session['user_email'] = email
                    request.session['user_role'] = 'member'

            messages.success(request, 'Selamat datang di AeroMiles!')
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

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT email, salutation, first_mid_name, last_name,
                   country_code, mobile_number, tanggal_lahir, kewarganegaraan
            FROM pengguna WHERE email = %s
        """, [user_email])
        pengguna = dict_fetchone(cursor)

        if role == 'member':
            cursor.execute("""
                SELECT email, nomor_member, tanggal_bergabung, id_tier, award_miles, total_miles
                FROM member WHERE email = %s
            """, [user_email])
            member_data = dict_fetchone(cursor)

        elif role == 'staf':
            cursor.execute("""
                SELECT email, id_staf, kode_maskapai
                FROM staf WHERE email = %s
            """, [user_email])
            staf_data = dict_fetchone(cursor)

    return render(request, 'dashboard.html', {
        'user_email': user_email,
        'role': role,
        'member': member_data,
        'staf': staf_data,
        'pengguna': pengguna,
    })


def profile(request):
    user_email, role = get_user_from_request(request)
    if not user_email:
        return redirect('login')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT email, salutation, first_mid_name, last_name,
                   country_code, mobile_number, tanggal_lahir, kewarganegaraan
            FROM pengguna WHERE email = %s
        """, [user_email])
        pengguna = dict_fetchone(cursor)

    if not pengguna:
        return redirect('login')

    member = None
    if role == 'member':
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT email, nomor_member, tanggal_bergabung, id_tier, award_miles, total_miles
                FROM member WHERE email = %s
            """, [user_email])
            member = dict_fetchone(cursor)

    if request.method == 'POST':
        salutation = request.POST.get('salutation', '')
        first_mid_name = request.POST.get('first_mid_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        country_code = request.POST.get('country_code', '').strip()
        mobile_number = request.POST.get('mobile_number', '').strip()
        tanggal_lahir = request.POST.get('tanggal_lahir', '') or None
        kewarganegaraan = request.POST.get('kewarganegaraan', '').strip()

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE pengguna
                    SET salutation = %s, first_mid_name = %s, last_name = %s,
                        country_code = %s, mobile_number = %s,
                        tanggal_lahir = %s, kewarganegaraan = %s
                    WHERE email = %s
                """, [salutation, first_mid_name, last_name, country_code,
                      mobile_number, tanggal_lahir, kewarganegaraan, user_email])
            messages.success(request, 'Profil berhasil diperbarui')
            return redirect('profile')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

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
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT password FROM pengguna WHERE email = %s
                    """, [user_email])
                    row = cursor.fetchone()
                    if not row:
                        messages.error(request, 'User tidak ditemukan')
                    elif row[0] == hash_password(old_password):
                        cursor.execute("""
                            UPDATE pengguna SET password = %s WHERE email = %s
                        """, [hash_password(new_password), user_email])
                        messages.success(request, 'Password berhasil diubah')
                        return redirect('profile')
                    else:
                        messages.error(request, 'Password lama salah')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')

    return render(request, 'change_password.html')


def manage_identity(request):
    user_email, role = get_user_from_request(request)
    if not user_email:
        return redirect('login')
    if role != 'member':
        return redirect('dashboard')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT nomor, jenis, negara_penerbit, tanggal_terbit, tanggal_habis
            FROM identitas
            WHERE email_member = %s
            ORDER BY tanggal_terbit DESC
        """, [user_email])
        identities = dict_fetchall(cursor)

    return render(request, 'manage_identity.html', {
        'identities': identities,
        'user_email': user_email,
    })


# =============================================================================
#  CRUD IDENTITY
# =============================================================================

from django.http import JsonResponse
from django.views.decorators.http import require_POST


def create_identity(request):
    user_email, role = get_user_from_request(request)

    if request.method == 'POST':
        nomor = request.POST.get('nomor', '').strip()
        jenis = request.POST.get('jenis', '')
        negara_penerbit = request.POST.get('negara_penerbit', '').strip()
        tanggal_terbit = request.POST.get('tanggal_terbit', '') or None
        tanggal_habis = request.POST.get('tanggal_habis', '') or None

        if not nomor or not jenis:
            messages.error(request, 'Nomor dokumen dan jenis wajib diisi')
        else:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT nomor FROM identitas WHERE nomor = %s", [nomor])
                    if cursor.fetchone():
                        messages.error(request, 'Nomor dokumen sudah terdaftar')
                    else:
                        cursor.execute("""
                            INSERT INTO identitas (nomor, email_member, jenis, negara_penerbit, tanggal_terbit, tanggal_habis)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, [nomor, user_email, jenis, negara_penerbit, tanggal_terbit, tanggal_habis])
                        messages.success(request, 'Identitas berhasil ditambahkan')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')

        return redirect('identity')

    return render(request, 'create_identity.html', {'user_email': user_email})


def edit_identity(request, identity_id):
    user_email, role = get_user_from_request(request)

    if request.method == 'GET':
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT nomor, jenis, negara_penerbit, tanggal_terbit, tanggal_habis
                FROM identitas WHERE nomor = %s
            """, [identity_id])
            identity = dict_fetchone(cursor)

        if not identity:
            return JsonResponse({'error': 'Identitas tidak ditemukan'}, status=404)

        return JsonResponse({'identity': {
            'nomor': identity['nomor'],
            'jenis': identity['jenis'],
            'negara_penerbit': identity['negara_penerbit'],
            'tanggal_terbit': str(identity['tanggal_terbit']) if identity['tanggal_terbit'] else '',
            'tanggal_habis': str(identity['tanggal_habis']) if identity['tanggal_habis'] else '',
        }})

    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT email_member FROM identitas WHERE nomor = %s", [identity_id])
                row = cursor.fetchone()
                if not row:
                    return JsonResponse({'error': 'Identitas tidak ditemukan'}, status=404)
                if row[0] != user_email:
                    return JsonResponse({'error': 'Unauthorized'}, status=403)

                cursor.execute("""
                    UPDATE identitas
                    SET jenis = %s, negara_penerbit = %s,
                        tanggal_terbit = %s, tanggal_habis = %s
                    WHERE nomor = %s
                """, [
                    request.POST.get('jenis', ''),
                    request.POST.get('negara_penerbit', '').strip(),
                    request.POST.get('tanggal_terbit', '') or None,
                    request.POST.get('tanggal_habis', '') or None,
                    identity_id
                ])
            return JsonResponse({'success': True, 'message': 'Identitas berhasil diperbarui'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid'}, status=405)


@require_POST
def delete_identity(request, identity_id):
    user_email, role = get_user_from_request(request)

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT email_member FROM identitas WHERE nomor = %s", [identity_id])
            row = cursor.fetchone()
            if row and row[0] == user_email:
                cursor.execute("DELETE FROM identitas WHERE nomor = %s", [identity_id])
                messages.success(request, 'Identitas berhasil dihapus')
    except Exception as e:
        messages.error(request, str(e))

    return redirect('identity')


# =============================================================================
#  CRUD MEMBER (Staf)
# =============================================================================

def manage_members(request):
    user_email, role = get_user_from_request(request)

    search = request.GET.get('search', '').strip()
    tier_filter = request.GET.get('tier', '')

    with connection.cursor() as cursor:
        query = """
            SELECT m.email, m.nomor_member, m.tanggal_bergabung,
                   m.id_tier, m.award_miles, m.total_miles
            FROM member m
            WHERE 1=1
        """
        params = []
        if search:
            query += " AND m.email ILIKE %s"
            params.append(f'%{search}%')
        if tier_filter:
            query += " AND m.id_tier = %s"
            params.append(tier_filter)
        query += " ORDER BY m.nomor_member"
        cursor.execute(query, params)
        members = dict_fetchall(cursor)

        cursor.execute("SELECT id_tier, nama FROM tier ORDER BY minimal_tier_miles")
        tiers = dict_fetchall(cursor)

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
        mobile_number = request.POST.get('mobile_number', '').strip()
        nationality = request.POST.get('nationality', '').strip()
        birth_date = request.POST.get('birth_date', '') or None

        if not email or not password or not last_name:
            return JsonResponse({'error': 'Email, password, dan last name wajib diisi'}, status=400)

        try:
            from datetime import date
            with connection.cursor() as cursor:
                cursor.execute("SELECT email FROM pengguna WHERE LOWER(email) = LOWER(%s)", [email])
                if cursor.fetchone():
                    return JsonResponse({'error': 'Email sudah terdaftar'}, status=400)

                cursor.execute("""
                    INSERT INTO pengguna (email, password, salutation, first_mid_name, last_name,
                        country_code, mobile_number, tanggal_lahir, kewarganegaraan)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [email, hash_password(password), salutation, first_mid_name, last_name,
                      country_code, mobile_number, birth_date, nationality])

                cursor.execute("SELECT COUNT(*) FROM member")
                member_count = cursor.fetchone()[0] + 1
                cursor.execute("""
                    INSERT INTO member (email, nomor_member, tanggal_bergabung, id_tier, award_miles, total_miles)
                    VALUES (%s, %s, %s, 'T01', 0, 0)
                """, [email, f'M{date.today().year}{member_count:04d}', date.today()])

            return JsonResponse({'success': True, 'message': f'Member {email} berhasil dibuat'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid'}, status=405)


def edit_member(request, member_id):
    member_id = str(member_id)
    user_email, role = get_user_from_request(request)

    if request.method == 'GET':
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT email, nomor_member, id_tier FROM member WHERE email = %s
            """, [member_id])
            member = dict_fetchone(cursor)

        if not member:
            return JsonResponse({'error': 'Member tidak ditemukan'}, status=404)
        return JsonResponse({'member': member})

    if request.method == 'POST':
        tier_id = request.POST.get('tier') or 'T01'
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id_tier FROM tier WHERE id_tier = %s", [tier_id])
                if not cursor.fetchone():
                    return JsonResponse({'error': 'Tier tidak valid'}, status=400)

                cursor.execute("""
                    UPDATE member SET id_tier = %s WHERE email = %s
                """, [tier_id, member_id])
            return JsonResponse({'success': True, 'message': 'Member berhasil diperbarui'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid'}, status=405)


@require_POST
def delete_member(request, member_id):
    member_id = str(member_id)
    user_email, role = get_user_from_request(request)

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT email FROM member WHERE email = %s", [member_id])
            if cursor.fetchone():
                cursor.execute("DELETE FROM member WHERE email = %s", [member_id])
                cursor.execute("DELETE FROM pengguna WHERE email = %s", [member_id])
                messages.success(request, 'Member berhasil dihapus')
            else:
                messages.error(request, 'Member tidak ditemukan')
    except Exception as e:
        messages.error(request, str(e))

    return redirect('manage_members')


# =============================================================================
#  CRUD MANAJEMEN MITRA (Staf)
# =============================================================================

def manage_partners(request):
    user_email, role = get_user_from_request(request)
    if role != 'staf':
        return redirect('dashboard')

    search = request.GET.get('search', '').strip()

    with connection.cursor() as cursor:
        query = """
            SELECT email_mitra, id_penyedia, nama_mitra, tanggal_kerja_sama
            FROM mitra
        """
        params = []
        if search:
            query += " WHERE nama_mitra ILIKE %s OR email_mitra ILIKE %s"
            params = [f'%{search}%', f'%{search}%']
        query += " ORDER BY nama_mitra"
        cursor.execute(query, params)
        mitra_list = dict_fetchall(cursor)

    return render(request, 'manage_partners.html', {
        'mitra_list': mitra_list,
        'search': search,
    })


def partner_detail(request, email):
    """Return detail mitra sebagai JSON untuk edit modal"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT email_mitra, id_penyedia, nama_mitra, tanggal_kerja_sama
            FROM mitra WHERE email_mitra = %s
        """, [email])
        mitra = dict_fetchone(cursor)

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
    """Buat mitra baru (sekaligus buat entri PENYEDIA baru)"""
    user_email, role = get_user_from_request(request)
    if role != 'staf':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    email_mitra = request.POST.get('email_mitra', '').strip()
    nama_mitra = request.POST.get('nama_mitra', '').strip()
    tanggal = request.POST.get('tanggal_kerja_sama', '').strip()

    if not all([email_mitra, nama_mitra, tanggal]):
        return JsonResponse({'error': 'Semua field wajib harus diisi'})

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT email_mitra FROM mitra WHERE email_mitra = %s", [email_mitra])
            if cursor.fetchone():
                return JsonResponse({'error': 'Email mitra sudah terdaftar'})

            cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM penyedia")
            new_id = cursor.fetchone()[0]

            cursor.execute("INSERT INTO penyedia (id) VALUES (%s)", [new_id])
            cursor.execute("""
                INSERT INTO mitra (email_mitra, id_penyedia, nama_mitra, tanggal_kerja_sama)
                VALUES (%s, %s, %s, %s)
            """, [email_mitra, new_id, nama_mitra, tanggal])

        return JsonResponse({'success': True, 'message': f'Mitra {nama_mitra} berhasil ditambahkan (ID Penyedia: {new_id})'})
    except Exception as e:
        return JsonResponse({'error': str(e)})


@require_POST
def edit_partner(request, email):
    """Update data mitra (kecuali email dan id_penyedia)"""
    user_email, role = get_user_from_request(request)
    if role != 'staf':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    nama_mitra = request.POST.get('nama_mitra', '').strip()
    tanggal = request.POST.get('tanggal_kerja_sama', '').strip()

    if not all([nama_mitra, tanggal]):
        return JsonResponse({'error': 'Semua field wajib harus diisi'})

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE mitra
                SET nama_mitra = %s, tanggal_kerja_sama = %s
                WHERE email_mitra = %s
            """, [nama_mitra, tanggal, email])
        return JsonResponse({'success': True, 'message': 'Mitra berhasil diperbarui'})
    except Exception as e:
        return JsonResponse({'error': str(e)})


@require_POST
def delete_partner(request, email):
    """Hapus mitra beserta penyedia terkait"""
    user_email, role = get_user_from_request(request)
    if role != 'staf':
        return redirect('dashboard')

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_penyedia FROM mitra WHERE email_mitra = %s", [email])
            row = cursor.fetchone()
            if not row:
                messages.error(request, 'Mitra tidak ditemukan.')
                return redirect('manage_partners')

            pid = row[0]
            cursor.execute("DELETE FROM mitra WHERE email_mitra = %s", [email])
            cursor.execute("DELETE FROM penyedia WHERE id = %s", [pid])

        messages.success(request, 'Mitra berhasil dihapus.')
    except Exception as e:
        messages.error(request, str(e))

    return redirect('manage_partners')
