from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .models import User


def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not email or not password:
            messages.error(request, 'Email dan password harus diisi')
            return render(request, 'login.html')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.email}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Email atau password salah')
    return render(request, 'login.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    role = request.GET.get('role', 'member')
    from features.flights.models import Airline
    airlines = Airline.objects.all() if role == 'staf' else []

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        salutation = request.POST.get('salutation', '').strip()
        first_mid_name = request.POST.get('first_mid_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        country_code = request.POST.get('country_code', '').strip()
        phone = request.POST.get('phone', '').strip()
        nationality = request.POST.get('nationality', '').strip()
        birth_date = request.POST.get('birth_date', '')
        role = request.POST.get('role', 'member')

        errors = []
        if not email:
            errors.append('Email harus diisi')
        if not password1:
            errors.append('Password harus diisi')
        if password1 != password2:
            errors.append('Password dan konfirmasi password tidak cocok')
        if not last_name:
            errors.append('Last Name harus diisi')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'register.html', {'role': role, 'airlines': airlines})

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email sudah terdaftar')
            return render(request, 'register.html', {'role': role, 'airlines': airlines})

        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password1,
                salutation=salutation,
                first_mid_name=first_mid_name,
                last_name=last_name,
                country_code=country_code,
                phone=phone,
                nationality=nationality,
                birth_date=birth_date or None,
                role=role
            )
            login(request, user)
            messages.success(request, f'Welcome to AeroMiles, {user.get_full_name() or user.email}!')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')

    return render(request, 'register.html', {'role': role, 'airlines': airlines})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Anda telah logout')
    return redirect('login')


@login_required
def dashboard(request):
    user = request.user
    from features.transactions.models import Transaction, ClaimMiles
    recent_transactions = Transaction.objects.filter(user=user)[:5]
    pending_claims_count = 0

    if user.role == 'staf':
        pending_claims_count = ClaimMiles.objects.filter(status='pending').count()
        approved_count = ClaimMiles.objects.filter(status='approved').count()
        rejected_count = ClaimMiles.objects.filter(status='rejected').count()
    else:
        pending_claims_count = ClaimMiles.objects.filter(user=user, status='pending').count()

    context = {
        'user': user,
        'recent_transactions': recent_transactions,
        'pending_claims_count': pending_claims_count,
    }

    if user.role == 'staf':
        context.update({
            'approved_count': approved_count,
            'rejected_count': rejected_count,
        })

    return render(request, 'dashboard.html', context)


@login_required
def profile(request):
    user = request.user
    from features.flights.models import Airline
    airlines = Airline.objects.all() if user.role == 'staf' else []

    if request.method == 'POST':
        user.salutation = request.POST.get('salutation', '').strip()
        user.first_mid_name = request.POST.get('first_mid_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.country_code = request.POST.get('country_code', '').strip()
        user.phone = request.POST.get('phone', '').strip()
        user.nationality = request.POST.get('nationality', '').strip()
        birth_date = request.POST.get('birth_date', '')
        user.birth_date = birth_date or None

        if user.role == 'staf':
            airline_id = request.POST.get('airline', '')
            if airline_id:
                user.airline_id = airline_id

        user.save()
        messages.success(request, 'Profil berhasil diperbarui')
        return redirect('profile')

    return render(request, 'profile.html', {'user': user, 'airlines': airlines})


@login_required
def change_password(request):
    user = request.user

    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password berhasil diubah')
            return redirect('profile')
        else:
            messages.error(request, 'Password lama salah atau password baru tidak valid')
    else:
        form = PasswordChangeForm(user)

    return render(request, 'change_password.html', {'form': form})


@login_required
def claim_miles(request):
    if request.user.role != 'member':
        return redirect('dashboard')
    from features.transactions.models import ClaimMiles
    claims = ClaimMiles.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'claim_miles.html', {'claims': claims})


@login_required
def transfer_miles(request):
    if request.user.role != 'member':
        return redirect('dashboard')
    from features.transactions.models import TransferMiles
    transfers = request.user.sent_transfers.all() | request.user.received_transfers.all()
    return render(request, 'transfer_miles.html', {'transfers': transfers})


@login_required
def redeem_rewards(request):
    if request.user.role != 'member':
        return redirect('dashboard')
    from features.rewards.models import Reward
    rewards = Reward.objects.filter(is_active=True)
    return render(request, 'redeem_rewards.html', {'rewards': rewards})


@login_required
def buy_packages(request):
    if request.user.role != 'member':
        return redirect('dashboard')
    from features.rewards.models import Package
    packages = Package.objects.filter(is_active=True)
    return render(request, 'buy_packages.html', {'packages': packages})


@login_required
def tier_info(request):
    if request.user.role != 'member':
        return redirect('dashboard')
    return render(request, 'tier_info.html', {'user': request.user})


@login_required
def manage_members(request):
    if request.user.role != 'staf':
        return redirect('dashboard')
    members = User.objects.filter(role='member')
    return render(request, 'manage_members.html', {'members': members})


@login_required
def manage_claims(request):
    if request.user.role != 'staf':
        return redirect('dashboard')
    from features.transactions.models import ClaimMiles
    claims = ClaimMiles.objects.order_by('-created_at')
    return render(request, 'manage_claims.html', {'claims': claims})


@login_required
def manage_rewards(request):
    if request.user.role != 'staf':
        return redirect('dashboard')
    from features.rewards.models import Reward
    rewards = Reward.objects.all()
    return render(request, 'manage_rewards.html', {'rewards': rewards})


@login_required
def manage_partners(request):
    if request.user.role != 'staf':
        return redirect('dashboard')
    return render(request, 'manage_partners.html')


@login_required
def transaction_report(request):
    if request.user.role != 'staf':
        return redirect('dashboard')
    from features.transactions.models import Transaction
    transactions = Transaction.objects.all().order_by('-created_at')[:100]
    return render(request, 'transaction_report.html', {'transactions': transactions})