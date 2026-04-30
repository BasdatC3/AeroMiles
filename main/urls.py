from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('features.accounts.urls')),
    path('rewards/', include('features.rewards.urls')),
    path('transactions/', include('features.transactions.urls')),
]