from datetime import date

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from main.auth_utils import get_session_user, role_required
from features.accounts.services import identity_service


@role_required('member')
def manage_identity(request):
    user_email = get_session_user(request)[0]
    identities = identity_service.list_for_member(user_email)

    today = date.today()
    for i in identities:
        i['is_expired'] = i['tanggal_habis'] < today

    return render(request, 'manage_identity.html', {
        'identities': identities,
        'user_email': user_email,
    })


@role_required('member')
def create_identity(request):
    user_email = get_session_user(request)[0]

    if request.method != 'POST':
        return redirect('identity')

    nomor = request.POST.get('nomor', '').strip()
    jenis = request.POST.get('jenis', '')
    negara_penerbit = request.POST.get('negara_penerbit', '').strip()
    tanggal_terbit = request.POST.get('tanggal_terbit', '')
    tanggal_habis = request.POST.get('tanggal_habis', '')

    if not all([nomor, jenis, negara_penerbit, tanggal_terbit, tanggal_habis]):
        messages.error(request, 'Semua field wajib diisi.')
        return redirect('identity')

    if identity_service.exists(nomor):
        messages.error(request, 'Nomor dokumen sudah terdaftar.')
        return redirect('identity')

    try:
        identity_service.create(
            nomor, user_email, jenis, negara_penerbit, tanggal_terbit, tanggal_habis,
        )
        messages.success(request, 'Identitas berhasil ditambahkan.')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')

    return redirect('identity')


def edit_identity(request, identity_id):
    user_email, role = get_session_user(request)
    if not user_email or role != 'member':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    identity = identity_service.get(identity_id)
    if not identity:
        return JsonResponse({'error': 'Identitas tidak ditemukan'}, status=404)
    if identity['email_member'] != user_email:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    if request.method == 'GET':
        return JsonResponse({'identity': {
            'nomor': identity['nomor'],
            'jenis': identity['jenis'],
            'negara_penerbit': identity['negara_penerbit'],
            'tanggal_terbit': str(identity['tanggal_terbit']),
            'tanggal_habis': str(identity['tanggal_habis']),
        }})

    if request.method == 'POST':
        jenis = request.POST.get('jenis', '')
        negara_penerbit = request.POST.get('negara_penerbit', '').strip()
        tanggal_terbit = request.POST.get('tanggal_terbit', '')
        tanggal_habis = request.POST.get('tanggal_habis', '')

        if not all([jenis, negara_penerbit, tanggal_terbit, tanggal_habis]):
            return JsonResponse({'error': 'Semua field wajib diisi'}, status=400)

        try:
            identity_service.update(identity_id, jenis, negara_penerbit,
                                    tanggal_terbit, tanggal_habis)
            return JsonResponse({'success': True, 'message': 'Identitas berhasil diperbarui'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@require_POST
@role_required('member')
def delete_identity(request, identity_id):
    user_email = get_session_user(request)[0]

    identity = identity_service.get(identity_id)
    if identity and identity['email_member'] == user_email:
        identity_service.delete(identity_id)
        messages.success(request, 'Identitas berhasil dihapus.')
    else:
        messages.error(request, 'Identitas tidak ditemukan.')

    return redirect('identity')
