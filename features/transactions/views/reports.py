from django.shortcuts import render

from main.auth_utils import role_required
from features.transactions.services import report_service


@role_required('staf')
def transaction_report(request):
    ctx = report_service.stats()
    ctx['transactions'] = report_service.recent_transactions()
    ctx['top_members'] = report_service.top_members()
    return render(request, 'transaction_report.html', ctx)
