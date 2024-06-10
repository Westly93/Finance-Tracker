from django.urls import path
from tracker import views


urlpatterns = [
    path("", views.index, name='index'),
    path('transactions_list/', views.transactions_list, name="transactions_list"),
]
