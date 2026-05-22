from django.urls import path

from .views.claims import (
    claim_miles, edit_claim, cancel_claim,
    manage_claims, approve_claim, reject_claim,
)
from .views.transfers import transfer_miles
from .views.reports import transaction_report


urlpatterns = [
    path('claim-miles/', claim_miles, name='claim_miles'),
    path('claim-miles/<int:claim_id>/edit/', edit_claim, name='edit_claim'),
    path('claim-miles/<int:claim_id>/cancel/', cancel_claim, name='cancel_claim'),
    path('transfer-miles/', transfer_miles, name='transfer_miles'),

    path('manage-claims/', manage_claims, name='manage_claims'),
    path('claims/approve/<int:id>/', approve_claim, name='approve_claim'),
    path('claims/reject/<int:id>/', reject_claim, name='reject_claim'),
    path('report/', transaction_report, name='transaction_report'),
]
