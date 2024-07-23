from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Transaction
from .forms import TransactionForm
from .filters import TransactionFilter
from django_htmx.http import retarget
from django.core.paginator import Paginator
# Create your views here.

from django.conf import settings

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
    paginator= Paginator(transactions_filter.qs, settings.PAGE_SIZE)
    
    total_income = transactions_filter.qs.get_total_income()
    total_expenses = transactions_filter.qs.get_total_expenses()

    context = {
        'transactions': paginator.page(1),
        "filter": transactions_filter,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_income": total_income - total_expenses
    }
    if request.htmx:
        return render(request, 'tracker/partials/transactions-list.html', context)
    return render(request, 'tracker/transactions_list.html', context)
@login_required
def get_transactions(request):
    page= request.GET.get("page", 1)
    transactions_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(
            user=request.user).select_related("category")
    )
    # transactions = Transaction.objects.filter(user=request.user).all()
    paginator= Paginator(transactions_filter.qs, settings.PAGE_SIZE)
    context={'transactions': paginator.page(page)}
    return render(request, 'tracker/partials/transactions-list.html#transactions-list', context)

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
            response=  render(request, 'tracker/partials/create_transaction.html', context)
            return retarget(response, '#transaction-block')
    form = TransactionForm()
    context = {
        "form": form
    }
    return render(request, 'tracker/partials/create_transaction.html', context)


@login_required
def update_transaction(request, pk):
    transaction= get_object_or_404(Transaction, pk=pk, user= request.user)
    if request.method== "POST":
        form= TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            context = {
                "message": "The Transaction was updated successfully!"
            }
            return render(request, 'tracker/partials/transaction-success.html', context)
        else:
            context= {
                'form':form,
                "transaction": transaction
            }
            response= render(request, 'tracker/partials/update-transaction.html', context)
            return retarget(response, "#block-transaction")
    form= TransactionForm(instance= transaction)
    context={
        'transaction': transaction,
        'form': form
    }
    return render(request, 'tracker/partials/update-transaction.html', context)
@login_required
def delete_transaction(request, pk):
    transaction= get_object_or_404(Transaction, pk=pk, user= request.user)
    transaction.delete()
    context = {
                "message": f"The { transaction.type } tansaction created on {transaction.date} was deleted successfully!"
            }
    return render(request, 'tracker/partials/transaction-success.html', context)
    