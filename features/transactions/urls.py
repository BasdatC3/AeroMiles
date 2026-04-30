from django.urls import path
from . import views

urlpatterns = [
    path('claim-miles/', views.claim_miles, name='claim_miles'),
    path('transfer-miles/', views.transfer_miles, name='transfer_miles'),
    path('manage-claims/', views.manage_claims, name='manage_claims'),
    path('claims/approve/<int:id>/', views.approve_claim, name='approve_claim'),
    path('claims/reject/<int:id>/', views.reject_claim, name='reject_claim'),
    path('report/', views.transaction_report, name='transaction_report'),
]