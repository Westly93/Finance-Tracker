from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Transaction
from .forms import TransactionForm
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


@login_required
def create_transaction(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            context = {
                "message": "The Transaction was created successfully!"
            }
            return render(request, 'tracker/partials/transaction-success.html', context)
        else:
            context = {
                "form": form
            }
            return render(request, 'tracker/partials/create_transaction.html', context)
    form = TransactionForm()
    context = {
        "form": form
    }
    return render(request, 'tracker/partials/create_transaction.html', context)
