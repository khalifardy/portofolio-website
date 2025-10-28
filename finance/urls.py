# finance/urls.py
from django.urls import path
from .views import (
    finance_dashboard,
    add_transaction,
    transactions,
    research_menu,
    edit_transaction,
    delete_transaction
) 

app_name = 'finance'

urlpatterns = [
   
    
    # ========================================
    # DASHBOARD URLs
    # ========================================
    path('', finance_dashboard, name='dashboard_finance'),
    path('dashboard_finance/', finance_dashboard, name='dashboard_finance'),
    
    # ========================================
    # TRANSACTION URLs
    # ========================================
    path('transactions/', transactions, name='transactions'),
    path('transactions/add/', add_transaction, name='add_transaction'),
    path('transactions/edit/<int:transaction_id>/', edit_transaction, name='edit_transaction'),
    path('transactions/delete/<int:transaction_id>/', delete_transaction, name='delete_transaction'),
    # ========================================
    # RESEARCH MENU URLs
    # ========================================
    path('research/', research_menu, name='research_menu'),
]