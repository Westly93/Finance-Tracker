from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Transaction
from .forms import TransactionForm
from .filters import TransactionFilter
from django_htmx.http import retarget
from django.core.paginator import Paginator
from .charting import income_expenses_bar, category_pie_chart
from .resources import TransactionResource
from django.http.response import HttpResponse
from tablib import Dataset
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
@login_required
def transactions_charts(request):
    transactions_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(
            user=request.user).select_related("category")
    )
    bar_chart= income_expenses_bar(transactions_filter.qs)
    income_category_pie= category_pie_chart(
        transactions_filter.qs.filter(type= 'income')
    )
    expenses_category_pie= category_pie_chart(
        transactions_filter.qs.filter(type= 'expense')
    )
    context= {
        'filter': transactions_filter,
        'income_expenses_bar': bar_chart.to_html(),
        'income_category_pie': income_category_pie.to_html(),
        'expenses_category_pie': expenses_category_pie.to_html()
    }
    if request.htmx:
        return render(request, 'tracker/partials/charts.html', context)
    return render(request, 'tracker/charts-container.html', context)
@login_required   
def export_transactions(request):
    if request.htmx:
        return HttpResponse(headers= {'HX-Redirect': request.get_full_path()})
    transactions_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(
            user=request.user).select_related("category")
    )
    data= TransactionResource().export(transactions_filter.qs)
    response= HttpResponse(data.csv)
    response['Content-Disposition']= 'attachement; filename= "transactions.csv"'
    return response
@login_required
def import_transactions(request):
    if request.method=='POST':
        file= request.FILES.get('file')
        resource= TransactionResource()
        dataset= Dataset()
        dataset.load(file.read().decode('utf-8'), format='csv')
        result= resource.import_data(dataset,user= request.user, dry_run= True)
        for row in result:
            for error in row.errors:
                print(error)
        if not result.has_errors():
            resource.import_data(dataset, dry_run= False)
            context={
                'message': f'{len(dataset)} transactions are loaded successfully'
            }
        else:
            context= {
                'message': "Sorry An Error Occured"
            }
        return render(request, 'tracker/partials/transaction-success.html', context)
    
    return render(request, 'tracker/partials/import_transactions.html')