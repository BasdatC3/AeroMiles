from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from main.auth_utils import get_session_user, role_required
from features.transactions.services import claim_service


@role_required('member')
def claim_miles(request):
    user_email = get_session_user(request)[0]

    if request.method == "POST":
        data = {
            'maskapai': request.POST.get('maskapai', '').strip(),
            'bandara_asal': request.POST.get('bandara_asal', '').strip(),
            'bandara_tujuan': request.POST.get('bandara_tujuan', '').strip(),
            'tanggal_penerbangan': request.POST.get('tanggal_penerbangan', '').strip(),
            'flight_number': request.POST.get('flight_number', '').strip(),
            'nomor_tiket': request.POST.get('nomor_tiket', '').strip(),
            'kelas_kabin': request.POST.get('kelas_kabin', 'Economy'),
            'pnr': request.POST.get('pnr', '').strip(),
        }

        if not all(data.values()):
            messages.error(request, "Semua field wajib diisi!")
            return redirect('claim_miles')
        if data['bandara_asal'] == data['bandara_tujuan']:
            messages.error(request, "Bandara asal dan tujuan tidak boleh sama!")
            return redirect('claim_miles')
        if claim_service.is_duplicate(user_email, data['flight_number'],
                                      data['tanggal_penerbangan'], data['nomor_tiket']):
            messages.error(request, "Klaim duplikat: penerbangan ini sudah pernah diajukan.")
            return redirect('claim_miles')

        try:
            claim_service.create(user_email, data)
            messages.success(request, "Klaim berhasil diajukan!")
        except Exception as e:
            messages.error(request, f"Gagal klaim: {str(e)}")

        return redirect('claim_miles')

    status_filter = request.GET.get('status', '')
    return render(request, 'claim_miles.html', {
        'claims': claim_service.list_for_member(user_email, status_filter),
        'maskapai_list': claim_service.list_maskapai(),
        'bandara_list': claim_service.list_bandara(),
        'status_filter': status_filter,
    })


def edit_claim(request, claim_id):
    user_email, role = get_session_user(request)
    if not user_email or role != 'member':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    claim = claim_service.get(claim_id)
    if not claim:
        return JsonResponse({'error': 'Klaim tidak ditemukan'}, status=404)
    if claim['email_member'] != user_email:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    if request.method == 'GET':
        return JsonResponse({'claim': {
            'id': claim['id'],
            'maskapai': claim['maskapai'],
            'bandara_asal': claim['bandara_asal'],
            'bandara_tujuan': claim['bandara_tujuan'],
            'tanggal_penerbangan': str(claim['tanggal_penerbangan']),
            'flight_number': claim['flight_number'],
            'nomor_tiket': claim['nomor_tiket'],
            'kelas_kabin': claim['kelas_kabin'],
            'pnr': claim['pnr'],
            'status_penerimaan': claim['status_penerimaan'],
        }})

    if request.method == 'POST':
        if claim['status_penerimaan'] != 'Menunggu':
            return JsonResponse({
                'error': "Hanya klaim berstatus 'Menunggu' yang dapat diedit.",
            }, status=400)

        data = {
            'maskapai': request.POST.get('maskapai', '').strip(),
            'bandara_asal': request.POST.get('bandara_asal', '').strip(),
            'bandara_tujuan': request.POST.get('bandara_tujuan', '').strip(),
            'tanggal_penerbangan': request.POST.get('tanggal_penerbangan', '').strip(),
            'flight_number': request.POST.get('flight_number', '').strip(),
            'nomor_tiket': request.POST.get('nomor_tiket', '').strip(),
            'kelas_kabin': request.POST.get('kelas_kabin', 'Economy'),
            'pnr': request.POST.get('pnr', '').strip(),
        }
        if not all(data.values()):
            return JsonResponse({'error': 'Semua field wajib diisi'}, status=400)

        try:
            claim_service.update(claim_id, data)
            return JsonResponse({'success': True, 'message': 'Klaim berhasil diperbarui'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@require_POST
@role_required('member')
def cancel_claim(request, claim_id):
    user_email = get_session_user(request)[0]

    claim = claim_service.get(claim_id)
    if not claim or claim['email_member'] != user_email:
        messages.error(request, 'Klaim tidak ditemukan.')
        return redirect('claim_miles')
    if claim['status_penerimaan'] != 'Menunggu':
        messages.error(request, "Hanya klaim 'Menunggu' yang dapat dibatalkan.")
        return redirect('claim_miles')

    try:
        claim_service.delete(claim_id)
        messages.success(request, 'Klaim berhasil dibatalkan.')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')

    return redirect('claim_miles')


@role_required('staf')
def manage_claims(request):
    status_filter = request.GET.get('status', '')
    maskapai_filter = request.GET.get('maskapai', '')

    return render(request, 'manage_claims.html', {
        'claims': claim_service.list_for_staff(status_filter, maskapai_filter),
        'maskapai_list': claim_service.list_maskapai(),
        'status_filter': status_filter,
        'maskapai_filter': maskapai_filter,
    })


@require_POST
@role_required('staf')
def approve_claim(request, id):
    user_email = get_session_user(request)[0]

    claim = claim_service.get(id)
    if not claim:
        messages.error(request, 'Klaim tidak ditemukan.')
        return redirect('manage_claims')
    if claim['status_penerimaan'] != 'Menunggu':
        messages.error(request, 'Klaim sudah diproses sebelumnya.')
        return redirect('manage_claims')

    try:
        miles = claim_service.approve(id, user_email, claim['email_member'],
                                      claim['kelas_kabin'])
        messages.success(request, f"Klaim disetujui. {miles} miles ditambahkan ke member.")
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')

    return redirect('manage_claims')


@require_POST
@role_required('staf')
def reject_claim(request, id):
    user_email = get_session_user(request)[0]

    claim = claim_service.get(id)
    if not claim:
        messages.error(request, 'Klaim tidak ditemukan.')
        return redirect('manage_claims')
    if claim['status_penerimaan'] != 'Menunggu':
        messages.error(request, 'Klaim sudah diproses sebelumnya.')
        return redirect('manage_claims')

    claim_service.reject(id, user_email)
    messages.success(request, 'Klaim berhasil ditolak.')
    return redirect('manage_claims')
