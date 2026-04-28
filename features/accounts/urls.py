from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('password/', views.change_password, name='change_password'),

    # Member views
    path('claim-miles/', views.claim_miles, name='claim_miles'),
    path('transfer-miles/', views.transfer_miles, name='transfer_miles'),
    path('redeem-rewards/', views.redeem_rewards, name='redeem_rewards'),
    path('buy-packages/', views.buy_packages, name='buy_packages'),
    path('tier-info/', views.tier_info, name='tier_info'),

    # Staff views
    path('members/', views.manage_members, name='manage_members'),
    path('claims/', views.manage_claims, name='manage_claims'),
    path('rewards/', views.manage_rewards, name='manage_rewards'),
    path('partners/', views.manage_partners, name='manage_partners'),
    path('report/', views.transaction_report, name='transaction_report'),
]