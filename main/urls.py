"""
URL routing untuk AeroMiles (TK03).

Tidak ada admin URLs karena Django admin bergantung pada ORM auth tables.
"""
from django.urls import path, include

urlpatterns = [
    path('', include('features.accounts.urls')),
    path('rewards/', include('features.rewards.urls')),
    path('transactions/', include('features.transactions.urls')),
]
