from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from main.auth_utils import get_session_user, role_required
from features.accounts.services import auth_service, member_service, profile_service


@role_required('staf')
def manage_members(request):
    tiers = profile_service.list_tiers()
    search = request.GET.get('search', '').strip()
    tier_filter = request.GET.get('tier', '')

    members = member_service.list_all()
    if search:
        s = search.lower()
        members = [m for m in members if
                   s in (m['email'] or '').lower()
                   or s in (m['first_mid_name'] or '').lower()
                   or s in (m['last_name'] or '').lower()
                   or s in (m['nomor_member'] or '').lower()]
    if tier_filter:
        members = [m for m in members if m['id_tier'] == tier_filter]

    return render(request, 'manage_members.html', {
        'members': members,
        'tiers': tiers,
        'search': search,
        'tier_filter': tier_filter,
    })


@require_POST
def create_member(request):
    _, role = get_session_user(request)
    if role != 'staf':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    data = {
        'email': request.POST.get('email', '').strip(),
        'password': request.POST.get('password', ''),
        'salutation': request.POST.get('salutation', 'Mr.'),
        'first_mid_name': request.POST.get('first_mid_name', '').strip(),
        'last_name': request.POST.get('last_name', '').strip(),
        'country_code': request.POST.get('country_code', '').strip(),
        'mobile_number': request.POST.get('phone', '').strip(),
        'kewarganegaraan': request.POST.get('nationality', '').strip(),
        'tanggal_lahir': request.POST.get('birth_date', ''),
    }

    if not data['email'] or not data['password'] or not data['last_name']:
        return JsonResponse({'error': 'Email, password, dan nama belakang wajib diisi'}, status=400)

    if auth_service.email_exists(data['email']):
        return JsonResponse({'error': 'Email sudah terdaftar'}, status=400)

    try:
        auth_service.create_pengguna(data)
        auth_service.create_member(data['email'])
        return JsonResponse({'success': True, 'message': f"Member {data['email']} berhasil dibuat"})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def edit_member(request, member_id):
    _, role = get_session_user(request)
    if role != 'staf':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    member = member_service.get(member_id)
    if not member:
        return JsonResponse({'error': 'Member tidak ditemukan'}, status=404)

    if request.method == 'GET':
        return JsonResponse({'member': {
            'email': member['email'],
            'nomor_member': member['nomor_member'],
            'id_tier': member['id_tier'],
        }})

    if request.method == 'POST':
        tier_id = request.POST.get('tier', 'T01')
        if not member_service.tier_exists(tier_id):
            return JsonResponse({'error': 'Tier tidak valid'}, status=400)
        try:
            member_service.update_tier(member_id, tier_id)
            return JsonResponse({'success': True, 'message': 'Member berhasil diperbarui'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@require_POST
@role_required('staf')
def delete_member(request, member_id):
    try:
        member_service.delete_cascade(str(member_id))
        messages.success(request, 'Member berhasil dihapus.')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    return redirect('manage_members')
