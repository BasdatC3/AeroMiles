from django.shortcuts import render, redirect
from django.contrib import messages
import hashlib


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
        try:
            from features.accounts.models import Pengguna, Member, Staf
            pengguna = Pengguna.objects.get(email=email, password=hashed)

            try:
                Member.objects.get(email=email)
                messages.success(request, 'Welcome back!')
                request.session['user_email'] = email
                request.session['user_role'] = 'member'
                return redirect('dashboard')
            except Member.DoesNotExist:
                pass

            try:
                Staf.objects.get(email=email)
                messages.success(request, 'Welcome back!')
                request.session['user_email'] = email
                request.session['user_role'] = 'staf'
                return redirect('dashboard')
            except Staf.DoesNotExist:
                pass

        except Pengguna.DoesNotExist:
            messages.error(request, 'Email atau password salah')

    return render(request, 'login.html')


def register(request):
    user_email, role = get_user_from_request(request)
    if user_email:
        return redirect('dashboard')

    from features.accounts.models import Tier, Maskapai
    tiers = Tier.objects.all()
    airlines = Maskapai.objects.all()

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

        from features.accounts.models import Pengguna
        if Pengguna.objects.filter(email=email).exists():
            messages.error(request, 'Email sudah terdaftar')
            return render(request, 'register.html', {
                'tiers': tiers, 'airlines': airlines, 'role': selected_role
            })

        try:
            from datetime import date
            from features.accounts.models import Member, Staf
            Pengguna.objects.create(
                email=email,
                password=hash_password(password1),
                salutation=salutation,
                first_mid_name=first_mid_name,
                last_name=last_name,
                country_code=country_code,
                mobile_number=mobile_number,
                tanggal_lahir=tanggal_lahir or None,
                kewarganegaraan=kewarganegaraan,
            )

            if selected_role == 'staf':
                airline_code = request.POST.get('airline', '')
                staff_count = Staf.objects.count() + 1
                Staf.objects.create(
                    email=email,
                    id_staf=f'SF{date.today().year}{staff_count:04d}',
                    kode_maskapai=airline_code,
                )
                messages.success(request, 'Selamat datang di AeroMiles!')
                request.session['user_email'] = email
                request.session['user_role'] = 'staf'
            else:
                Member.objects.create(
                    email=email,
                    nomor_member=f'M{str(date.today().year)}{Member.objects.count()+1:04d}',
                    tanggal_bergabung=date.today(),
                    id_tier='BASIC',
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

    from features.accounts.models import Pengguna, Member, Staf
    member_data = None
    staf_data = None
    pengguna = None

    try:
        pengguna = Pengguna.objects.get(email=user_email)
    except Pengguna.DoesNotExist:
        pass

    if role == 'member':
        try:
            member_data = Member.objects.get(email=user_email)
        except Member.DoesNotExist:
            pass
    elif role == 'staf':
        try:
            staf_data = Staf.objects.get(email=user_email)
        except Staf.DoesNotExist:
            pass

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

    from features.accounts.models import Pengguna, Member
    try:
        pengguna = Pengguna.objects.get(email=user_email)
    except Pengguna.DoesNotExist:
        return redirect('login')

    try:
        member = Member.objects.get(email=user_email)
    except Member.DoesNotExist:
        member = None

    if request.method == 'POST':
        pengguna.salutation = request.POST.get('salutation', '')
        pengguna.first_mid_name = request.POST.get('first_mid_name', '').strip()
        pengguna.last_name = request.POST.get('last_name', '').strip()
        pengguna.country_code = request.POST.get('country_code', '').strip()
        pengguna.mobile_number = request.POST.get('mobile_number', '').strip()
        tanggal_lahir = request.POST.get('tanggal_lahir', '')
        pengguna.tanggal_lahir = tanggal_lahir or None
        pengguna.kewarganegaraan = request.POST.get('kewarganegaraan', '').strip()
        pengguna.save()
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
    if not user_email:
        return redirect('login')

    if request.method == 'POST':
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not old_password or not new_password:
            messages.error(request, 'Password lama dan baru harus diisi')
        elif new_password != confirm_password:
            messages.error(request, 'Password baru dan konfirmasi tidak cocok')
        else:
            from features.accounts.models import Pengguna
            try:
                pengguna = Pengguna.objects.get(email=user_email)
                if pengguna.password == hash_password(old_password):
                    pengguna.password = hash_password(new_password)
                    pengguna.save()
                    messages.success(request, 'Password berhasil diubah')
                    return redirect('profile')
                else:
                    messages.error(request, 'Password lama salah')
            except Pengguna.DoesNotExist:
                messages.error(request, 'User tidak ditemukan')

    return render(request, 'change_password.html')


def manage_identity(request):
    user_email, role = get_user_from_request(request)
    from features.accounts.models import Identitas

    identities = []
    if user_email and role == 'member':
        identities = Identitas.objects.filter(email_member=user_email)

    return render(request, 'manage_identity.html', {'identities': identities})


# ========== CRUD Identity ==========
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from features.accounts.models import Identitas


def create_identity(request):
    user_email, role = get_user_from_request(request)

    if request.method == 'POST' and user_email and role == 'member':
        nomor = request.POST.get('nomor', '').strip()
        jenis = request.POST.get('jenis', '')
        negara_penerbit = request.POST.get('negara_penerbit', '').strip()
        tanggal_terbit = request.POST.get('tanggal_terbit', '')
        tanggal_habis = request.POST.get('tanggal_habis', '')

        if not nomor or not jenis:
            return JsonResponse({'error': 'Nomor dokumen dan jenis wajib diisi'}, status=400)

        if Identitas.objects.filter(nomor=nomor).exists():
            return JsonResponse({'error': 'Nomor dokumen sudah terdaftar'}, status=400)

        try:
            Identitas.objects.create(
                nomor=nomor,
                email_member=user_email,
                jenis=jenis,
                negara_penerbit=negara_penerbit,
                tanggal_terbit=tanggal_terbit or None,
                tanggal_habis=tanggal_habis or None,
            )
            return JsonResponse({'success': True, 'message': 'Identitas berhasil ditambahkan'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid'}, status=405)


def edit_identity(request, identity_id):
    identity = get_object_or_404(Identitas, nomor=identity_id)
    user_email, role = get_user_from_request(request)

    if request.method == 'GET':
        return JsonResponse({
            'identity': {
                'nomor': identity.nomor,
                'jenis': identity.jenis,
                'negara_penerbit': identity.negara_penerbit,
                'tanggal_terbit': str(identity.tanggal_terbit) if identity.tanggal_terbit else '',
                'tanggal_habis': str(identity.tanggal_habis) if identity.tanggal_habis else '',
            }
        })

    if request.method == 'POST':
        if user_email != identity.email_member:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        identity.jenis = request.POST.get('jenis', '')
        identity.negara_penerbit = request.POST.get('negara_penerbit', '').strip()
        identity.tanggal_terbit = request.POST.get('tanggal_terbit', '') or None
        identity.tanggal_habis = request.POST.get('tanggal_habis', '') or None

        try:
            identity.save()
            return JsonResponse({'success': True, 'message': 'Identitas berhasil diperbarui'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid'}, status=405)


@require_POST
def delete_identity(request, identity_id):
    user_email, role = get_user_from_request(request)
    identity = get_object_or_404(Identitas, nomor=identity_id)

    if user_email == identity.email_member:
        identity.delete()
        messages.success(request, 'Identitas berhasil dihapus')

    return redirect('identity')


# ========== CRUD Member (Staf) ==========
from features.accounts.models import Member


def manage_members(request):
    user_email, role = get_user_from_request(request)
    from features.accounts.models import Tier

    if role != 'staf':
        return redirect('dashboard')

    members = Member.objects.all()
    tiers = Tier.objects.all()
    search = request.GET.get('search', '').strip()
    tier_filter = request.GET.get('tier', '')

    if search:
        members = members.filter(email__icontains=search)
    if tier_filter:
        members = members.filter(id_tier=tier_filter)

    return render(request, 'manage_members.html', {
        'members': members,
        'tiers': tiers,
        'search': search,
        'tier_filter': tier_filter,
    })


def create_member(request):
    user_email, role = get_user_from_request(request)
    from features.accounts.models import Pengguna

    if role != 'staf':
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        salutation = request.POST.get('salutation', '')
        first_mid_name = request.POST.get('first_mid_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        country_code = request.POST.get('country_code', '').strip()
        mobile_number = request.POST.get('mobile_number', '').strip()
        nationality = request.POST.get('nationality', '').strip()
        birth_date = request.POST.get('birth_date', '')

        if not email or not password or not last_name:
            return JsonResponse({'error': 'Email, password, dan last name wajib diisi'}, status=400)

        if Pengguna.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email sudah terdaftar'}, status=400)

        try:
            from datetime import date
            Pengguna.objects.create(
                email=email,
                password=hash_password(password),
                salutation=salutation,
                first_mid_name=first_mid_name,
                last_name=last_name,
                country_code=country_code,
                mobile_number=mobile_number,
                tanggal_lahir=birth_date or None,
                kewarganegaraan=nationality,
            )

            Member.objects.create(
                email=email,
                nomor_member=f'M{str(date.today().year)}{Member.objects.count()+1:04d}',
                tanggal_bergabung=date.today(),
                id_tier='BASIC',
            )

            return JsonResponse({'success': True, 'message': f'Member {email} berhasil dibuat'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid'}, status=405)


def edit_member(request, member_id):
    member_id = str(member_id)
    user_email, role = get_user_from_request(request)

    if role != 'staf':
        return redirect('dashboard')

    member = get_object_or_404(Member, email=member_id)

    if request.method == 'GET':
        return JsonResponse({
            'member': {
                'email': member.email,
                'nomor_member': member.nomor_member,
                'id_tier': member.id_tier,
            }
        })

    if request.method == 'POST':
        member.id_tier = request.POST.get('tier', 'BASIC')

        try:
            member.save()
            return JsonResponse({'success': True, 'message': 'Member berhasil diperbarui'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid'}, status=405)


@require_POST
def delete_member(request, member_id):
    member_id = str(member_id)
    user_email, role = get_user_from_request(request)
    from features.accounts.models import Pengguna

    if role != 'staf':
        return redirect('dashboard')

    try:
        member = Member.objects.get(email=member_id)
        member.delete()
        try:
            pengguna = Pengguna.objects.get(email=member_id)
            pengguna.delete()
        except:
            pass
        messages.success(request, 'Member berhasil dihapus')
    except Member.DoesNotExist:
        messages.error(request, 'Member tidak ditemukan')

    return redirect('manage_members')