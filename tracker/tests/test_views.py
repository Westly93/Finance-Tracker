import pytest
from datetime import timedelta, datetime
from django.urls import reverse
from tracker.models import Category


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
