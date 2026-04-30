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
    if not user_email or role != 'member':
        return redirect('login')

    from features.accounts.models import Hadiah, Member
    rewards = Hadiah.objects.all()
    member = Member.objects.get(email=user_email)

    return render(request, 'redeem_rewards.html', {'rewards': rewards, 'member': member})


def buy_packages(request):
    """Beli Package - untuk Member"""
    user_email, role = get_user_from_request(request)
    if not user_email or role != 'member':
        return redirect('login')

    from features.accounts.models import AwardMilesPackage, Member
    packages = AwardMilesPackage.objects.all()
    member = Member.objects.get(email=user_email)

    return render(request, 'buy_packages.html', {'packages': packages, 'member': member})


def tier_info(request):
    """Info Tier - untuk Member"""
    user_email, role = get_user_from_request(request)
    if not user_email or role != 'member':
        return redirect('login')

    from features.accounts.models import Tier
    tiers = Tier.objects.all()

    return render(request, 'tier_info.html', {'tiers': tiers})


def manage_rewards(request):
    """Kelola Hadiah - untuk Staf"""
    user_email, role = get_user_from_request(request)
    if role != 'staf':
        return redirect('dashboard')

    from features.accounts.models import Hadiah
    rewards = Hadiah.objects.all()

    return render(request, 'manage_rewards.html', {'rewards': rewards})