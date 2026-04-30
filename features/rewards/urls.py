from django.urls import path
from . import views

urlpatterns = [
    path('redeem-rewards/', views.redeem_rewards, name='redeem_rewards'),
    path('buy-packages/', views.buy_packages, name='buy_packages'),
    path('tier-info/', views.tier_info, name='tier_info'),
    path('manage-rewards/', views.manage_rewards, name='manage_rewards'),

    # CRUD
    path('hadiah/next-kode/', views.hadiah_next_kode, name='hadiah_next_kode'),
    path('hadiah/<str:kode>/detail/', views.hadiah_detail, name='hadiah_detail'),
    path('hadiah/create/', views.create_hadiah, name='create_hadiah'),
    path('hadiah/<str:kode>/edit/', views.edit_hadiah, name='edit_hadiah'),
    path('hadiah/<str:kode>/delete/', views.delete_hadiah, name='delete_hadiah'),
]