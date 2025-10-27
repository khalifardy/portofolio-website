# finance/urls.py
from django.urls import path
from .views import (
    finance_dashboard,
    add_transaction,
    transactions,
    research_menu
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
    
    # ========================================
    # RESEARCH MENU URLs
    # ========================================
    path('research/', research_menu, name='research_menu'),
]