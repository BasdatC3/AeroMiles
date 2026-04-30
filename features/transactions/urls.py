from django.urls import path
from . import views

urlpatterns = [
    path('claim-miles/', views.claim_miles, name='claim_miles'),
    path('transfer-miles/', views.transfer_miles, name='transfer_miles'),
    path('manage-claims/', views.manage_claims, name='manage_claims'),
    path('manage-partners/', views.manage_partners, name='manage_partners'),
    path('report/', views.transaction_report, name='transaction_report'),
]