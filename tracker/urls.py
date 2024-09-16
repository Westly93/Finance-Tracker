from django.urls import path
from tracker import views


urlpatterns = [
    path("", views.index, name='index'),
    path('transactions_list/', views.transactions_list, name="transactions_list"),
    path('create_transaction/', views.create_transaction,name="create_transaction"),
    path('update-transaction/<int:pk>/', views.update_transaction, name="update_transaction"),
    path('delete-transaction/<int:pk>/', views.delete_transaction, name="delete_transaction"),
    path('transactions-charts/', views.transactions_charts, name="transactions_charts"),
    path('get-transactions/', views.get_transactions, name='get-transactions'),
    path('transactions/export/', views.export_transactions, name='export-transactions'),
    path('transactions/import/', views.import_transactions, name='import-transactions'),

]
