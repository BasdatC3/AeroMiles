from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from main.auth_utils import get_session_user, role_required
from features.accounts.services import partner_service


@role_required('staf')
def manage_partners(request):
    search = request.GET.get('search', '').strip()
    mitra_list = partner_service.list_all()

    if search:
        s = search.lower()
        mitra_list = [m for m in mitra_list if
                      s in (m['email_mitra'] or '').lower()
                      or s in (m['nama_mitra'] or '').lower()]

    return render(request, 'manage_partners.html', {
        'mitra_list': mitra_list,
        'search': search,
    })


def partner_detail(request, email):
    mitra = partner_service.get(email)
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
    _, role = get_session_user(request)
    if role != 'staf':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    email_mitra = request.POST.get('email_mitra', '').strip()
    nama_mitra = request.POST.get('nama_mitra', '').strip()
    tanggal = request.POST.get('tanggal_kerja_sama', '').strip()

    if not all([email_mitra, nama_mitra, tanggal]):
        return JsonResponse({'error': 'Semua field wajib diisi'}, status=400)
    if partner_service.email_exists(email_mitra):
        return JsonResponse({'error': 'Email mitra sudah terdaftar'}, status=400)

    try:
        new_id = partner_service.next_penyedia_id()
        partner_service.create_penyedia(new_id)
        partner_service.create(email_mitra, new_id, nama_mitra, tanggal)
        return JsonResponse({
            'success': True,
            'message': f'Mitra {nama_mitra} berhasil ditambahkan (ID Penyedia: {new_id})',
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_POST
def edit_partner(request, email):
    _, role = get_session_user(request)
    if role != 'staf':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    nama_mitra = request.POST.get('nama_mitra', '').strip()
    tanggal = request.POST.get('tanggal_kerja_sama', '').strip()

    if not all([nama_mitra, tanggal]):
        return JsonResponse({'error': 'Semua field wajib diisi'}, status=400)

    try:
        partner_service.update(email, nama_mitra, tanggal)
        return JsonResponse({'success': True, 'message': 'Mitra berhasil diperbarui'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_POST
@role_required('staf')
def delete_partner(request, email):
    mitra = partner_service.get(email)
    if not mitra:
        messages.error(request, 'Mitra tidak ditemukan.')
        return redirect('manage_partners')

    try:
        partner_service.delete(email, mitra['id_penyedia'])
        messages.success(request, 'Mitra berhasil dihapus.')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')

    return redirect('manage_partners')
