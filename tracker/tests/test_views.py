import pytest
from datetime import timedelta, datetime
from django.urls import reverse
from tracker.models import Category, Transaction
from pytest_django.asserts import assertTemplateUsed


@pytest.mark.django_db
def test_total_values_appear_on_the_list_page(user_transactions, client):
    # get the user
    user = user_transactions[0].user
    client.force_login(user)
    income_total = sum(
        t.amount for t in user_transactions if t.type == 'income')
    expenses_total = sum(
        t.amount for t in user_transactions if t.type == 'expense')
    net_income = income_total - expenses_total
    response = client.get(reverse('transactions_list'))

    assert response.context['total_income'] == income_total
    assert response.context['total_expenses'] == expenses_total
    assert response.context['net_income'] == net_income
    # force login the user


@pytest.mark.django_db
def test_transaction_type_filter(user_transactions, client):
    # get the user
    user = user_transactions[0].user
    # force user login
    client.force_login(user)
    # test the income filter
    GET_params = {
        "transaction_type": "income"
    }

    response = client.get(reverse('transactions_list'), GET_params)
    qs = response.context['filter'].qs
    assert all(
        t.type == 'income' for t in qs
    )
    GET_params = {
        "transaction_type": "expense"
    }

    response = client.get(reverse('transactions_list'), GET_params)
    qs = response.context['filter'].qs
    assert all(
        t.type == 'expense' for t in qs
    )


@pytest.mark.django_db
def test_start_end_date_filter(user_transactions, client):
    # get the user
    user = user_transactions[0].user
    # force user login
    client.force_login(user)
    # test the income filter
    # start date cuttoff
    start_date_cutoff = datetime.now().date() - timedelta(days=120)
    GET_params = {
        "start_date": start_date_cutoff
    }

    response = client.get(reverse('transactions_list'), GET_params)
    qs = response.context['filter'].qs
    for t in qs:
        assert start_date_cutoff <= t.date

    end_date_cutoff = datetime.now().date() - timedelta(days=20)
    GET_params = {
        "end_date": end_date_cutoff
    }

    response = client.get(reverse('transactions_list'), GET_params)
    qs = response.context['filter'].qs
    for t in qs:
        assert end_date_cutoff >= t.date


@pytest.mark.django_db
def test_category_filter(user_transactions, client):
    # get the user
    user = user_transactions[0].user
    # force user login
    client.force_login(user)
    category_pks = Category.objects.all()[:2].values_list('pk', flat=True)
    GET_params = {
        "category": category_pks
    }
    response = client.get(reverse('transactions_list'), GET_params)
    qs = response.context['filter'].qs
    for t in qs:
        assert t.category.pk in category_pks
        
        
@pytest.mark.django_db
def test_create_transaction_request(user, transaction_dict_params, client):
    #force login the user 
    client.force_login(user)
    # get the user transaction count 
    transaction_count= Transaction.objects.filter(user= user).count()
    
    #send request with transaction data
    headers={
        "HTTP_HX-Request": 'true'
    }
    response= client.post(reverse("create_transaction"), transaction_dict_params, **headers)
    assert Transaction.objects.filter(user=user).count()== transaction_count + 1
    
    assertTemplateUsed(response, 'tracker/partials/transaction-success.html')
    
    
    
@pytest.mark.django_db
def test_cannot_add_transaction_with_negative_amount(user, transaction_dict_params, client):
    #force login the user 
    client.force_login(user)
    # get the user transaction count 
    user_transaction_count= Transaction.objects.filter(user= user).count()
    
    headers= {
        "HTTP_HX-Request": "true"
    }
    
    # change the transaction amount to negative 
    transaction_dict_params['amount']= -66
    #send the request 
    response= client.post(reverse('create_transaction'), transaction_dict_params, **headers)
    
    assert Transaction.objects.filter(user= user).count()==user_transaction_count
    assertTemplateUsed(response, "tracker/partials/create_transaction.html")
    assert "HX-Retarget" in response.headers
    
    
@pytest.mark.django_db
def test_cannot_add_transaction_with_future_dates(user, transaction_dict_params, client):
    #force login the user 
    client.force_login(user)
    # get the user transaction count 
    user_transaction_count= Transaction.objects.filter(user= user).count()
    
    headers= {
        "HTTP_HX-Request": "true"
    }
    #change the date to an invalidate date which is the future date
    transaction_dict_params['date']= datetime.now().date()+timedelta(days=2)
    
    response= client.post(reverse('create_transaction'), transaction_dict_params, **headers)
    
    assert Transaction.objects.filter(user= user).count()==user_transaction_count
    assertTemplateUsed(response, "tracker/partials/create_transaction.html")
    assert "HX-Retarget" in response.headers
    
@pytest.mark.django_db
def test_update_transaction_request(user, transaction_dict_params, client):
    #force login the user 
    client.force_login(user)
    
    assert Transaction.objects.filter(user= user).count()==1
    headers= {
        "HTTP_HX-Request": "true"
    }
    new_date= datetime.now().date() - timedelta(days=2)
    transaction_dict_params['amount']=20
    transaction_dict_params['date']= new_date
    transaction= Transaction.objects.filter(user=user).first()
    response= client.post(reverse("update_transaction", kwargs={"pk": transaction.pk}), transaction_dict_params, **headers)
    transaction= Transaction.objects.filter(user= user).first()
    assertTemplateUsed(response, 'tracker/partials/transaction-success.html')
    assert Transaction.objects.filter(user= user).count() == 1
    assert transaction.amount == 20
    assert transaction.date==new_date
    
@pytest.mark.django_db
def test_cannot_update_transaction_with_negative_amount(user, transaction_dict_params, client):
    #force login the user 
    client.force_login(user)
    
    assert Transaction.objects.filter(user= user).count()==1
    
    transaction_dict_params['amount']= -44
    
    transaction= Transaction.objects.filter(user= user).first()
    response= client.post(
        reverse("update_transaction", kwargs={'pk': transaction.pk}), transaction_dict_params
    )
    transaction= Transaction.objects.filter(user= user).first()
    assertTemplateUsed(response, 'tracker/partials/update-transaction.html')
    assert Transaction.objects.filter(user= user).count() == 1
    assert transaction.amount != -44

@pytest.mark.django_db
def test_delete_transaction_request(user, transaction_dict_params, client):
    #force login the user 
    client.force_login(user)
    
    assert Transaction.objects.filter(user= user).count()==1
    transaction= Transaction.objects.filter(user= user).first()
    headers= {
        "HTTP_HX-Request": "true"
    }
    client.delete(reverse("delete_transaction", kwargs={'pk': transaction.pk}), **headers)
    assert Transaction.objects.filter(user=user).count()==0