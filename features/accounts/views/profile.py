from django.shortcuts import render, redirect
from django.contrib import messages

from main.auth_utils import get_session_user, login_required
from features.accounts.services import profile_service


@login_required
def profile(request):
    user_email, role = get_session_user(request)

    pengguna = profile_service.get_pengguna(user_email)
    if not pengguna:
        return redirect('login')

    if request.method == 'POST':
        data = {
            'salutation': request.POST.get('salutation', ''),
            'first_mid_name': request.POST.get('first_mid_name', '').strip(),
            'last_name': request.POST.get('last_name', '').strip(),
            'country_code': request.POST.get('country_code', '').strip(),
            'mobile_number': request.POST.get('mobile_number', '').strip(),
            'tanggal_lahir': request.POST.get('tanggal_lahir', ''),
            'kewarganegaraan': request.POST.get('kewarganegaraan', '').strip(),
        }
        try:
            profile_service.update_pengguna(user_email, data)
            if role == 'staf':
                kode_maskapai = request.POST.get('kode_maskapai', '').strip()
                if kode_maskapai:
                    profile_service.update_staf_maskapai(user_email, kode_maskapai)
            messages.success(request, 'Profil berhasil diperbarui')
            return redirect('profile')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    return render(request, 'profile.html', {
        'pengguna': pengguna,
        'member': profile_service.get_member(user_email),
        'staf': profile_service.get_staf(user_email),
        'airlines': profile_service.list_airlines(),
        'user_email': user_email,
        'role': role,
    })
