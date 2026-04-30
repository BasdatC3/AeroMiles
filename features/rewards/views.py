from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST


def get_user_from_request(request):
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    return user_email, user_role


def redeem_rewards(request):
    """Redeem Hadiah - untuk Member"""
    user_email, role = get_user_from_request(request)
    
    from features.accounts.models import Hadiah, Member
    rewards = Hadiah.objects.all()
    member = Member.objects.get(email=user_email)

    return render(request, 'redeem_rewards.html', {'rewards': rewards, 'member': member})


def buy_packages(request):
    """Beli Package - untuk Member"""
    user_email, role = get_user_from_request(request)
    
    from features.accounts.models import AwardMilesPackage, Member
    packages = AwardMilesPackage.objects.all()
    member = Member.objects.get(email=user_email)

    return render(request, 'buy_packages.html', {'packages': packages, 'member': member})


def tier_info(request):
    """Info Tier - untuk Member"""
    user_email, role = get_user_from_request(request)
    
    from features.accounts.models import Tier
    tiers = Tier.objects.all()

    return render(request, 'tier_info.html', {'tiers': tiers})


def manage_rewards(request):
    """Kelola Hadiah & Penyedia - untuk Staf"""
    user_email, role = get_user_from_request(request)
    if role != 'staf':
        return redirect('dashboard')

    from features.accounts.models import Hadiah, Penyedia, Maskapai, Mitra
    from datetime import date

    search = request.GET.get('search', '').strip()
    penyedia_filter = request.GET.get('penyedia', '')
    status_filter = request.GET.get('status', '')

    # Build penyedia info map: id -> {nama, tipe}
    maskapai_ids = set(Maskapai.objects.values_list('id_penyedia', flat=True))
    mitra_map = {m.id_penyedia: m.nama_mitra for m in Mitra.objects.all()}
    maskapai_map = {m.id_penyedia: m.nama_maskapai for m in Maskapai.objects.all()}

    hadiah_qs = Hadiah.objects.all().order_by('kode_hadiah')
    today = date.today()

    hadiah_list = []
    for h in hadiah_qs:
        pid = h.id_penyedia
        if pid in maskapai_ids:
            tipe = 'airline'
            nama_penyedia = maskapai_map.get(pid, f'Penyedia {pid}')
        else:
            tipe = 'partner'
            nama_penyedia = mitra_map.get(pid, f'Penyedia {pid}')

        is_expired = h.program_end < today

        # Apply filters
        if search and search.lower() not in h.nama.lower():
            continue
        if penyedia_filter and tipe != penyedia_filter:
            continue
        if status_filter == 'active' and is_expired:
            continue
        if status_filter == 'expired' and not is_expired:
            continue

        h.tipe_penyedia = tipe
        h.nama_penyedia = nama_penyedia
        h.is_expired = is_expired
        hadiah_list.append(h)

    # All hadiah for stats (unfiltered)
    all_hadiah = Hadiah.objects.all()
    active_count = sum(1 for h in all_hadiah if h.program_end >= today)
    expired_count = sum(1 for h in all_hadiah if h.program_end < today)

    # Build penyedia_list for dropdowns
    penyedia_list = []
    for m in Maskapai.objects.all():
        if m.id_penyedia:
            penyedia_list.append({'id': m.id_penyedia, 'nama': m.nama_maskapai, 'tipe': 'airline'})
    for m in Mitra.objects.all():
        penyedia_list.append({'id': m.id_penyedia, 'nama': m.nama_mitra, 'tipe': 'partner'})

    return render(request, 'manage_rewards.html', {
        'hadiah_list': hadiah_list,
        'penyedia_list': penyedia_list,
        'search': search,
        'penyedia_filter': penyedia_filter,
        'status_filter': status_filter,
        'total_count': all_hadiah.count(),
        'active_count': active_count,
        'expired_count': expired_count,
    })


def hadiah_next_kode(request):
    """Return kode hadiah berikutnya untuk ditampilkan di form"""
    from features.accounts.models import Hadiah
    last = Hadiah.objects.order_by('-kode_hadiah').first()
    if last:
        try:
            num = int(last.kode_hadiah.split('-')[1]) + 1
        except (IndexError, ValueError):
            num = 1
    else:
        num = 1
    return JsonResponse({'kode': f'RWD-{num:03d}'})


def hadiah_detail(request, kode):
    """Return detail hadiah sebagai JSON untuk edit modal"""
    from features.accounts.models import Hadiah
    try:
        h = Hadiah.objects.get(kode_hadiah=kode)
        return JsonResponse({'hadiah': {
            'kode_hadiah': h.kode_hadiah,
            'nama': h.nama,
            'miles': h.miles,
            'deskripsi': h.deskripsi or '',
            'valid_start_date': str(h.valid_start_date),
            'program_end': str(h.program_end),
            'id_penyedia': h.id_penyedia,
        }})
    except Hadiah.DoesNotExist:
        return JsonResponse({'error': 'Hadiah tidak ditemukan'}, status=404)


@require_POST
def create_hadiah(request):
    """Buat hadiah baru"""
    user_email, role = get_user_from_request(request)
    if role != 'staf':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    from features.accounts.models import Hadiah
    from django.db import connection

    nama = request.POST.get('nama', '').strip()
    id_penyedia = request.POST.get('id_penyedia', '').strip()
    miles = request.POST.get('miles', '').strip()
    deskripsi = request.POST.get('deskripsi', '').strip()
    valid_start = request.POST.get('valid_start_date', '').strip()
    program_end = request.POST.get('program_end', '').strip()

    if not all([nama, id_penyedia, miles, valid_start, program_end]):
        return JsonResponse({'error': 'Semua field wajib harus diisi'})

    # Generate kode
    last = Hadiah.objects.order_by('-kode_hadiah').first()
    try:
        num = int(last.kode_hadiah.split('-')[1]) + 1 if last else 1
    except (IndexError, ValueError, AttributeError):
        num = 1
    kode = f'RWD-{num:03d}'

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO hadiah (kode_hadiah, nama, miles, deskripsi, valid_start_date, program_end, id_penyedia)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                [kode, nama, int(miles), deskripsi, valid_start, program_end, int(id_penyedia)]
            )
        return JsonResponse({'success': True, 'message': f'Hadiah {kode} berhasil ditambahkan'})
    except Exception as e:
        return JsonResponse({'error': str(e)})


@require_POST
def edit_hadiah(request, kode):
    """Update hadiah"""
    user_email, role = get_user_from_request(request)
    if role != 'staf':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    from django.db import connection

    nama = request.POST.get('nama', '').strip()
    id_penyedia = request.POST.get('id_penyedia', '').strip()
    miles = request.POST.get('miles', '').strip()
    deskripsi = request.POST.get('deskripsi', '').strip()
    valid_start = request.POST.get('valid_start_date', '').strip()
    program_end = request.POST.get('program_end', '').strip()

    if not all([nama, id_penyedia, miles, valid_start, program_end]):
        return JsonResponse({'error': 'Semua field wajib harus diisi'})

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE hadiah SET nama=%s, miles=%s, deskripsi=%s,
                   valid_start_date=%s, program_end=%s, id_penyedia=%s
                   WHERE kode_hadiah=%s""",
                [nama, int(miles), deskripsi, valid_start, program_end, int(id_penyedia), kode]
            )
        return JsonResponse({'success': True, 'message': 'Hadiah berhasil diperbarui'})
    except Exception as e:
        return JsonResponse({'error': str(e)})


@require_POST
def delete_hadiah(request, kode):
    """Hapus hadiah (hanya yang sudah kadaluarsa)"""
    user_email, role = get_user_from_request(request)
    
    from features.accounts.models import Hadiah
    from datetime import date
    from django.db import connection

    try:
        h = Hadiah.objects.get(kode_hadiah=kode)
        if h.program_end >= date.today():
            messages.error(request, 'Hanya hadiah yang sudah kadaluarsa yang dapat dihapus.')
            return redirect('manage_rewards')
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM hadiah WHERE kode_hadiah=%s", [kode])
        messages.success(request, f'Hadiah {kode} berhasil dihapus.')
    except Hadiah.DoesNotExist:
        messages.error(request, 'Hadiah tidak ditemukan.')

    return redirect('manage_rewards')