from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import date

from main.db import execute_query, execute_write
from features.accounts.views import get_user_from_request as get_session_user


def redeem_rewards(request):
    user_email, role = get_session_user(request)

    rewards = execute_query("SELECT * FROM hadiah ORDER BY kode_hadiah", fetch_all=True) or []

    member = execute_query(
        "SELECT * FROM member WHERE email = %s",
        (user_email,),
        fetch_one=True
    )

    return render(request, 'redeem_rewards.html', {'rewards': rewards, 'member': member})


def buy_packages(request):
    user_email, role = get_session_user(request)

    packages = execute_query("SELECT * FROM award_miles_package ORDER BY id", fetch_all=True) or []

    member = execute_query(
        "SELECT * FROM member WHERE email = %s",
        (user_email,),
        fetch_one=True
    )

    return render(request, 'buy_packages.html', {'packages': packages, 'member': member})


def tier_info(request):
    user_email, role = get_session_user(request)

    tiers = execute_query("SELECT * FROM tier ORDER BY minimal_tier_miles", fetch_all=True) or []

    return render(request, 'tier_info.html', {'tiers': tiers})


def manage_rewards(request):
    user_email, role = get_session_user(request)
    if role != 'staf':
        return redirect('dashboard')

    search = request.GET.get('search', '').strip()
    penyedia_filter = request.GET.get('penyedia', '')
    status_filter = request.GET.get('status', '')

    maskapai_ids = set()
    for m in execute_query("SELECT id_penyedia FROM maskapai", fetch_all=True) or []:
        if m['id_penyedia']:
            maskapai_ids.add(m['id_penyedia'])

    mitra_map = {}
    for m in execute_query("SELECT id_penyedia, nama_mitra FROM mitra", fetch_all=True) or []:
        mitra_map[m['id_penyedia']] = m['nama_mitra']

    maskapai_map = {}
    for m in execute_query("SELECT id_penyedia, nama_maskapai FROM maskapai", fetch_all=True) or []:
        maskapai_map[m['id_penyedia']] = m['nama_maskapai']

    all_hadiah = execute_query("SELECT * FROM hadiah ORDER BY kode_hadiah", fetch_all=True) or []
    today = date.today()

    hadiah_list = []
    for h in all_hadiah:
        pid = h['id_penyedia']
        if pid in maskapai_ids:
            tipe = 'airline'
            nama_penyedia = maskapai_map.get(pid, f'Penyedia {pid}')
        else:
            tipe = 'partner'
            nama_penyedia = mitra_map.get(pid, f'Penyedia {pid}')

        is_expired = h['program_end'] < today

        if search and search.lower() not in h['nama'].lower():
            continue
        if penyedia_filter and tipe != penyedia_filter:
            continue
        if status_filter == 'active' and is_expired:
            continue
        if status_filter == 'expired' and not is_expired:
            continue

        h['tipe_penyedia'] = tipe
        h['nama_penyedia'] = nama_penyedia
        h['is_expired'] = is_expired
        hadiah_list.append(h)

    active_count = sum(1 for h in all_hadiah if h['program_end'] >= today)
    expired_count = sum(1 for h in all_hadiah if h['program_end'] < today)

    penyedia_list = []
    for m in execute_query("SELECT id_penyedia, nama_maskapai FROM maskapai", fetch_all=True) or []:
        if m['id_penyedia']:
            penyedia_list.append({'id': m['id_penyedia'], 'nama': m['nama_maskapai'], 'tipe': 'airline'})
    for m in execute_query("SELECT id_penyedia, nama_mitra FROM mitra", fetch_all=True) or []:
        penyedia_list.append({'id': m['id_penyedia'], 'nama': m['nama_mitra'], 'tipe': 'partner'})

    return render(request, 'manage_rewards.html', {
        'hadiah_list': hadiah_list,
        'penyedia_list': penyedia_list,
        'search': search,
        'penyedia_filter': penyedia_filter,
        'status_filter': status_filter,
        'total_count': len(all_hadiah),
        'active_count': active_count,
        'expired_count': expired_count,
    })


def hadiah_next_kode(request):
    last = execute_query("SELECT kode_hadiah FROM hadiah ORDER BY kode_hadiah DESC LIMIT 1", fetch_one=True)
    if last:
        try:
            num = int(last['kode_hadiah'].split('-')[1]) + 1
        except (IndexError, ValueError):
            num = 1
    else:
        num = 1
    return JsonResponse({'kode': f'RWD-{num:03d}'})


def hadiah_detail(request, kode):
    h = execute_query(
        "SELECT * FROM hadiah WHERE kode_hadiah = %s",
        (kode,),
        fetch_one=True
    )

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
    user_email, role = get_session_user(request)
    if role != 'staf':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    nama = request.POST.get('nama', '').strip()
    id_penyedia = request.POST.get('id_penyedia', '').strip()
    miles = request.POST.get('miles', '').strip()
    deskripsi = request.POST.get('deskripsi', '').strip()
    valid_start = request.POST.get('valid_start_date', '').strip()
    program_end = request.POST.get('program_end', '').strip()

    if not all([nama, id_penyedia, miles, valid_start, program_end]):
        return JsonResponse({'error': 'Semua field wajib harus diisi'})

    last = execute_query("SELECT kode_hadiah FROM hadiah ORDER BY kode_hadiah DESC LIMIT 1", fetch_one=True)
    try:
        num = int(last['kode_hadiah'].split('-')[1]) + 1 if last else 1
    except (IndexError, ValueError):
        num = 1
    kode = f'RWD-{num:03d}'

    try:
        execute_write(
            """INSERT INTO hadiah (kode_hadiah, nama, miles, deskripsi, valid_start_date, program_end, id_penyedia)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (kode, nama, int(miles), deskripsi, valid_start, program_end, int(id_penyedia))
        )
        return JsonResponse({'success': True, 'message': f'Hadiah {kode} berhasil ditambahkan'})
    except Exception as e:
        return JsonResponse({'error': str(e)})


@require_POST
def edit_hadiah(request, kode):
    user_email, role = get_session_user(request)
    if role != 'staf':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    nama = request.POST.get('nama', '').strip()
    id_penyedia = request.POST.get('id_penyedia', '').strip()
    miles = request.POST.get('miles', '').strip()
    deskripsi = request.POST.get('deskripsi', '').strip()
    valid_start = request.POST.get('valid_start_date', '').strip()
    program_end = request.POST.get('program_end', '').strip()

    if not all([nama, id_penyedia, miles, valid_start, program_end]):
        return JsonResponse({'error': 'Semua field wajib harus diisi'})

    try:
        execute_write(
            """UPDATE hadiah SET nama = %s, miles = %s, deskripsi = %s,
               valid_start_date = %s, program_end = %s, id_penyedia = %s
               WHERE kode_hadiah = %s""",
            (nama, int(miles), deskripsi, valid_start, program_end, int(id_penyedia), kode)
        )
        return JsonResponse({'success': True, 'message': 'Hadiah berhasil diperbarui'})
    except Exception as e:
        return JsonResponse({'error': str(e)})


@require_POST
def delete_hadiah(request, kode):
    _, _ = get_session_user(request)

    h = execute_query(
        "SELECT program_end FROM hadiah WHERE kode_hadiah = %s",
        (kode,),
        fetch_one=True
    )

    if not h:
        messages.error(request, 'Hadiah tidak ditemukan.')
        return redirect('manage_rewards')

    if h['program_end'] >= date.today():
        messages.error(request, 'Hanya hadiah yang sudah kadaluarsa yang dapat dihapus.')
        return redirect('manage_rewards')

    try:
        execute_write("DELETE FROM hadiah WHERE kode_hadiah = %s", (kode,))
        messages.success(request, f'Hadiah {kode} berhasil dihapus.')
    except Exception as e:
        messages.error(request, str(e))

    return redirect('manage_rewards')