from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST


def get_user_from_request(request):
    user_email = request.session.get('user_email')
    user_role = request.session.get('user_role')
    return user_email, user_role


def claim_miles(request):
    """Klaim Miles - untuk Member"""
    user_email, role = get_user_from_request(request)
    if not user_email or role != 'member':
        return redirect('login')

    from features.accounts.models import ClaimMissingMiles
    claims = ClaimMissingMiles.objects.filter(email_member=user_email).order_by('-timestamp')

    return render(request, 'claim_miles.html', {'claims': claims})


def transfer_miles(request):
    """Transfer Miles - untuk Member"""
    user_email, role = get_user_from_request(request)
    if not user_email or role != 'member':
        return redirect('login')

    from features.accounts.models import TransferMiles
    transfers = TransferMiles.objects.filter(email_member_1=user_email).order_by('-timestamp')

    return render(request, 'transfer_miles.html', {'transfers': transfers})


def manage_claims(request):
    """Kelola Klaim - untuk Staf"""
    user_email, role = get_user_from_request(request)
    if role != 'staf':
        return redirect('dashboard')

    from features.accounts.models import ClaimMissingMiles
    claims = ClaimMissingMiles.objects.all().order_by('-timestamp')
    status_filter = request.GET.get('status', '')

    if status_filter:
        claims = claims.filter(status_penerimaan=status_filter)

    return render(request, 'manage_claims.html', {
        'claims': claims,
        'status_filter': status_filter,
    })


def manage_partners(request):
    """Kelola Mitra - untuk Staf"""
    user_email, role = get_user_from_request(request)
    if role != 'staf':
        return redirect('dashboard')

    from features.accounts.models import Mitra
    partners = Mitra.objects.all()

    return render(request, 'manage_partners.html', {'partners': partners})


def transaction_report(request):
    """Laporan Transaksi - untuk Staf"""
    user_email, role = get_user_from_request(request)
    if role != 'staf':
        return redirect('dashboard')

    from features.accounts.models import Member, ClaimMissingMiles, Redeem
    stats = {
        'total_members': Member.objects.count(),
        'total_claims': ClaimMissingMiles.objects.count(),
        'pending_claims': ClaimMissingMiles.objects.filter(status_penerimaan='Menunggu').count(),
        'approved_claims': ClaimMissingMiles.objects.filter(status_penerimaan='Disetujui').count(),
        'rejected_claims': ClaimMissingMiles.objects.filter(status_penerimaan='Ditolak').count(),
        'total_redeems': Redeem.objects.count(),
    }

    return render(request, 'transaction_report.html', stats)