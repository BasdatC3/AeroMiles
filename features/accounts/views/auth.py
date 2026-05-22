from django.shortcuts import render, redirect
from django.contrib import messages

from main.auth_utils import get_session_user, hash_password, login_required
from features.accounts.services import auth_service, profile_service


def landing(request):
    if get_session_user(request)[0]:
        return redirect('dashboard')
    return render(request, 'landing.html')


def login_view(request):
    if get_session_user(request)[0]:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not email or not password:
            messages.error(request, 'Email dan password harus diisi')
            return render(request, 'login.html')

        if not auth_service.find_user_by_credentials(email, password):
            messages.error(request, 'Email atau password salah')
            return render(request, 'login.html')

        role = auth_service.get_role(email)
        if not role:
            messages.error(request, 'Akun terdaftar tetapi belum punya peran.')
            return render(request, 'login.html')

        request.session['user_email'] = email
        request.session['user_role'] = role
        messages.success(request, 'Welcome back!')
        return redirect('dashboard')

    return render(request, 'login.html')


def register(request):
    if get_session_user(request)[0]:
        return redirect('dashboard')

    tiers = profile_service.list_tiers()
    airlines = profile_service.list_airlines()
    selected_role = request.GET.get('role', 'member')
    ctx = {'tiers': tiers, 'airlines': airlines, 'role': selected_role}

    if request.method != 'POST':
        return render(request, 'register.html', ctx)

    selected_role = request.POST.get('role', selected_role)
    ctx['role'] = selected_role

    data = {
        'email': request.POST.get('email', '').strip(),
        'password': request.POST.get('password1', ''),
        'salutation': request.POST.get('salutation', 'Mr.'),
        'first_mid_name': request.POST.get('first_mid_name', '').strip(),
        'last_name': request.POST.get('last_name', '').strip(),
        'country_code': request.POST.get('country_code', '').strip(),
        'mobile_number': request.POST.get('mobile_number', '').strip(),
        'tanggal_lahir': request.POST.get('tanggal_lahir', ''),
        'kewarganegaraan': request.POST.get('kewarganegaraan', '').strip(),
    }
    password2 = request.POST.get('password2', '')
    airline = request.POST.get('airline', '')

    errors = []
    if not data['email']:
        errors.append('Email harus diisi')
    if not data['password']:
        errors.append('Password harus diisi')
    if data['password'] != password2:
        errors.append('Password dan konfirmasi password tidak cocok')
    if not data['last_name']:
        errors.append('Nama Belakang harus diisi')
    if selected_role == 'staf' and not airline:
        errors.append('Kode Maskapai wajib dipilih')

    if errors:
        for e in errors:
            messages.error(request, e)
        return render(request, 'register.html', ctx)

    if auth_service.email_exists(data['email']):
        messages.error(request, 'Email sudah terdaftar')
        return render(request, 'register.html', ctx)

    try:
        auth_service.create_pengguna(data)
        if selected_role == 'staf':
            auth_service.create_staf(data['email'], airline)
            request.session['user_role'] = 'staf'
        else:
            auth_service.create_member(data['email'])
            request.session['user_role'] = 'member'
        request.session['user_email'] = data['email']
        messages.success(request, 'Selamat datang di AeroMiles!')
        return redirect('dashboard')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return render(request, 'register.html', ctx)


def logout_view(request):
    request.session.flush()
    messages.success(request, 'Anda telah logout')
    return redirect('login')


@login_required
def change_password(request):
    user_email = get_session_user(request)[0]

    if request.method != 'POST':
        return render(request, 'change_password.html')

    old_password = request.POST.get('old_password', '')
    new_password = request.POST.get('new_password', '')
    confirm_password = request.POST.get('confirm_password', '')

    if not old_password or not new_password:
        messages.error(request, 'Password lama dan baru harus diisi')
    elif new_password != confirm_password:
        messages.error(request, 'Password baru dan konfirmasi tidak cocok')
    else:
        stored = auth_service.get_password(user_email)
        if stored == hash_password(old_password):
            auth_service.update_password(user_email, new_password)
            messages.success(request, 'Password berhasil diubah')
            return redirect('profile')
        else:
            messages.error(request, 'Password lama salah')

    return render(request, 'change_password.html')
