from datetime import date

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from main.auth_utils import get_session_user, role_required
from features.rewards.services import reward_service


@role_required('staf')
def manage_rewards(request):
    search = request.GET.get('search', '').strip()
    penyedia_filter = request.GET.get('penyedia', '')
    status_filter = request.GET.get('status', '')

    all_hadiah = reward_service.list_all()
    annotated = reward_service.annotate_with_provider(list(all_hadiah))

    hadiah_list = []
    for h in annotated:
        if search and search.lower() not in (h['nama'] or '').lower():
            continue
        if penyedia_filter and h['tipe_penyedia'] != penyedia_filter:
            continue
        if status_filter == 'active' and h['is_expired']:
            continue
        if status_filter == 'expired' and not h['is_expired']:
            continue
        hadiah_list.append(h)

    today = date.today()
    active_count = sum(1 for h in all_hadiah if h['program_end'] >= today)
    expired_count = sum(1 for h in all_hadiah if h['program_end'] < today)

    return render(request, 'manage_rewards.html', {
        'hadiah_list': hadiah_list,
        'penyedia_list': reward_service.list_all_penyedia(),
        'search': search,
        'penyedia_filter': penyedia_filter,
        'status_filter': status_filter,
        'total_count': len(all_hadiah),
        'active_count': active_count,
        'expired_count': expired_count,
    })


def hadiah_next_kode(request):
    return JsonResponse({'kode': reward_service.next_kode()})


def hadiah_detail(request, kode):
    h = reward_service.get(kode)
    if not h:
        return JsonResponse({'error': 'Hadiah tidak ditemukan'}, status=404)
    return JsonResponse({'hadiah': {
        'kode_hadiah': h['kode_hadiah'],
        'nama': h['nama'],
        'miles': h['miles'],
        'deskripsi': h['deskripsi'] or '',
        'valid_start_date': str(h['valid_start_date']),
        'program_end': str(h['program_end']),
        'id_penyedia': h['id_penyedia'],
    }})


@require_POST
def create_hadiah(request):
    _, role = get_session_user(request)
    if role != 'staf':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    nama = request.POST.get('nama', '').strip()
    id_penyedia = request.POST.get('id_penyedia', '').strip()
    miles = request.POST.get('miles', '').strip()
    deskripsi = request.POST.get('deskripsi', '').strip()
    valid_start = request.POST.get('valid_start_date', '').strip()
    program_end = request.POST.get('program_end', '').strip()

    if not all([nama, id_penyedia, miles, valid_start, program_end]):
        return JsonResponse({'error': 'Semua field wajib diisi'}, status=400)

    try:
        reward_service.create(
            nama, int(miles), deskripsi, valid_start, program_end, int(id_penyedia),
        )
        return JsonResponse({'success': True, 'message': 'Hadiah berhasil ditambahkan'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_POST
def edit_hadiah(request, kode):
    _, role = get_session_user(request)
    if role != 'staf':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    nama = request.POST.get('nama', '').strip()
    id_penyedia = request.POST.get('id_penyedia', '').strip()
    miles = request.POST.get('miles', '').strip()
    deskripsi = request.POST.get('deskripsi', '').strip()
    valid_start = request.POST.get('valid_start_date', '').strip()
    program_end = request.POST.get('program_end', '').strip()

    if not all([nama, id_penyedia, miles, valid_start, program_end]):
        return JsonResponse({'error': 'Semua field wajib diisi'}, status=400)

    try:
        reward_service.update(
            kode, nama, int(miles), deskripsi, valid_start, program_end, int(id_penyedia),
        )
        return JsonResponse({'success': True, 'message': 'Hadiah berhasil diperbarui'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_POST
@role_required('staf')
def delete_hadiah(request, kode):
    h = reward_service.get(kode)
    if not h:
        messages.error(request, 'Hadiah tidak ditemukan.')
        return redirect('manage_rewards')

    if not reward_service.is_expired(h):
        messages.error(request, 'Hanya hadiah yang sudah kadaluarsa yang dapat dihapus.')
        return redirect('manage_rewards')

    try:
        reward_service.delete(kode)
        messages.success(request, f'Hadiah {kode} berhasil dihapus.')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')

    return redirect('manage_rewards')
