from django.urls import path

from .views.redeem import redeem_rewards
from .views.packages import buy_packages
from .views.tier import tier_info
from .views.rewards import (
    manage_rewards, hadiah_next_kode, hadiah_detail,
    create_hadiah, edit_hadiah, delete_hadiah,
)


urlpatterns = [
    path('redeem-rewards/', redeem_rewards, name='redeem_rewards'),
    path('buy-packages/', buy_packages, name='buy_packages'),
    path('tier-info/', tier_info, name='tier_info'),

    path('manage-rewards/', manage_rewards, name='manage_rewards'),
    path('hadiah/next-kode/', hadiah_next_kode, name='hadiah_next_kode'),
    path('hadiah/<str:kode>/detail/', hadiah_detail, name='hadiah_detail'),
    path('hadiah/create/', create_hadiah, name='create_hadiah'),
    path('hadiah/<str:kode>/edit/', edit_hadiah, name='edit_hadiah'),
    path('hadiah/<str:kode>/delete/', delete_hadiah, name='delete_hadiah'),
]
