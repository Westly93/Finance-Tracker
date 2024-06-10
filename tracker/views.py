from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Transaction
from .filters import TransactionFilter

# Create your views here.


def index(request):
    return render(request, 'tracker/index.html')


@login_required
def transactions_list(request):
    transactions_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(
            user=request.user).select_related("category")
    )
    # transactions = Transaction.objects.filter(user=request.user).all()
    total_income = transactions_filter.qs.get_total_income()
    total_expenses = transactions_filter.qs.get_total_expenses()

    context = {
        "filter": transactions_filter,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_income": total_income - total_expenses
    }
    if request.htmx:
        return render(request, 'tracker/partials/transactions-list.html', context)
    return render(request, 'tracker/transactions_list.html', context)
