from django.urls import path
from . import views

urlpatterns = [
    path('redeem-rewards/', views.redeem_rewards, name='redeem_rewards'),
    path('buy-packages/', views.buy_packages, name='buy_packages'),
    path('tier-info/', views.tier_info, name='tier_info'),
    path('manage-rewards/', views.manage_rewards, name='manage_rewards'),
]