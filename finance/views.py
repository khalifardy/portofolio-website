# finance/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Transaction, Category, Budget, ResearchExpense
import json




# ========================================
# DASHBOARD VIEWS
# ========================================

@login_required
def finance_dashboard(request):
    """
    Dashboard utama finance dengan statistik dan grafik
    """
    # Ambil parameter filter bulan dari URL
    month_str = request.GET.get('month', timezone.now().strftime('%Y-%m'))
    
    # Parse month string ke datetime
    try:
        filter_date = datetime.strptime(month_str, '%Y-%m')
    except:
        filter_date = timezone.now()
    
    # Hitung total pemasukan bulan ini
    income_total = Transaction.objects.filter(
        user=request.user,
        type='income',
        date__year=filter_date.year,
        date__month=filter_date.month
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Hitung total pengeluaran bulan ini
    expense_total = Transaction.objects.filter(
        user=request.user,
        type='expense',
        date__year=filter_date.year,
        date__month=filter_date.month
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Hitung saldo (income - expense)
    balance = income_total - expense_total
    
    # Ambil transaksi terbaru (10 transaksi)
    recent_transactions = Transaction.objects.filter(
        user=request.user,
        date__year=filter_date.year,
        date__month=filter_date.month
    ).order_by('-date', '-created_at')[:10]
    
    # Data untuk grafik mingguan
    weeks_data = get_weekly_data(request.user, filter_date)
    
    # Data untuk grafik kategori pengeluaran
    category_data = get_category_breakdown(request.user, filter_date)
    
    context = {
        'income_total': income_total,
        'expense_total': expense_total,
        'balance': balance,
        'recent_transactions': recent_transactions,
        'current_month': filter_date,
        'weeks_data': json.dumps(weeks_data),
        'category_data': json.dumps(category_data),
    }
    
    return render(request, 'finance/finance_dashboard.html', context)


# ========================================
# TRANSACTION VIEWS
# ========================================

@login_required
def transactions(request):
    """
    Halaman daftar semua transaksi dengan filter
    """
    # Ambil semua transaksi user
    transactions_list = Transaction.objects.filter(user=request.user)
    
    # Filter berdasarkan tipe (income/expense)
    type_filter = request.GET.get('type')
    if type_filter:
        transactions_list = transactions_list.filter(type=type_filter)
    
    # Filter berdasarkan bulan
    month_filter = request.GET.get('month')
    if month_filter:
        try:
            date = datetime.strptime(month_filter, '%Y-%m')
            transactions_list = transactions_list.filter(
                date__year=date.year,
                date__month=date.month
            )
        except:
            pass
    
    # Filter berdasarkan kategori
    category_filter = request.GET.get('category')
    if category_filter:
        transactions_list = transactions_list.filter(category_id=category_filter)
    
    # Order by date descending
    transactions_list = transactions_list.order_by('-date', '-created_at')
    
        # Hitung total pemasukan bulan ini
    income_total = transactions_list.filter(
        type='income'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Hitung total pengeluaran bulan ini
    expense_total = transactions_list.filter(
        type='expense',
        ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'transactions': transactions_list,
        'categories': Category.objects.filter(user=request.user),
        'income_total': income_total,
        'expense_total': expense_total
    }
    
    return render(request, 'finance/transactions.html', context)


@login_required
def add_transaction(request):
    """
    View untuk menambah transaksi baru
    """
    if request.method == 'POST':
        # Ambil data dari form
        transaction_type = request.POST.get('type')
        amount = request.POST.get('amount')
        category_id = request.POST.get('category')
        description = request.POST.get('description', '')
        date = request.POST.get('date', timezone.now().date())
        
        # Buat transaksi baru
        Transaction.objects.create(
            user=request.user,
            type=transaction_type,
            amount=amount,
            category_id=category_id if category_id else None,
            description=description,
            date=date
        )
        
        messages.success(request, 'Transaksi berhasil ditambahkan!')
        return redirect('finance:dashboard_finance')
    
    # GET request - tampilkan form
    categories = Category.objects.filter(user=request.user)
    context = {
        'categories': categories,
        'today': timezone.now().date()
    }
    
    return render(request, 'finance/add_transaction.html', context)


# ========================================
# RESEARCH MENU VIEWS
# ========================================

@login_required
def research_menu(request):
    """
    Menu untuk riset berbagai bidang:
    - AI & Machine Learning
    - Fisika
    - Matematika
    - Engineering
    - Astronomi
    """
    # Ambil field dari parameter URL (default: ai)
    field = request.GET.get('field', 'ai')
    
    # Ambil semua research expenses untuk field ini
    expenses = ResearchExpense.objects.filter(
        user=request.user, 
        field=field
    ).order_by('-date')
    
    # Hitung total pengeluaran untuk field ini
    total_spent = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'field': field,
        'expenses': expenses,
        'total_spent': total_spent,
        'research_fields': ResearchExpense.RESEARCH_FIELDS,
    }
    
    return render(request, 'finance/research.html', context)


# ========================================
# HELPER FUNCTIONS
# ========================================

def get_weekly_data(user, month):
    """
    Ambil data transaksi per minggu dalam bulan tertentu
    untuk grafik bar chart mingguan
    
    Returns: List of dict dengan format:
    [
        {'week': 'Week 1', 'income': 1000000, 'expense': 500000},
        {'week': 'Week 2', 'income': 1500000, 'expense': 800000},
        ...
    ]
    """
    weeks = []
    start_date = month.replace(day=1)
    
    # Loop untuk maksimal 5 minggu
    for week_num in range(5):
        week_start = start_date + timedelta(days=week_num * 7)
        week_end = week_start + timedelta(days=6)
        
        # Jangan proses jika sudah lewat bulan ini
        if week_start.month != month.month:
            break
        
        # Hitung income untuk minggu ini
        income = Transaction.objects.filter(
            user=user,
            type='income',
            date__range=[week_start, week_end]
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Hitung expense untuk minggu ini
        expense = Transaction.objects.filter(
            user=user,
            type='expense',
            date__range=[week_start, week_end]
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        weeks.append({
            'week': f'Week {week_num + 1}',
            'income': float(income),
            'expense': float(expense)
        })
    
    return weeks


def get_category_breakdown(user, month):
    """
    Breakdown pengeluaran per kategori untuk bulan tertentu
    untuk grafik pie chart
    
    Returns: List of dict dengan format:
    [
        {'name': 'Makanan', 'value': 500000, 'color': '#ef4444'},
        {'name': 'Transportasi', 'value': 300000, 'color': '#f59e0b'},
        ...
    ]
    """
    categories = []
    
    # Query untuk aggregate pengeluaran per kategori
    expense_by_category = Transaction.objects.filter(
        user=user,
        type='expense',
        date__year=month.year,
        date__month=month.month
    ).values(
        'category__name', 
        'category__color'
    ).annotate(
        total=Sum('amount')
    )
    
    # Format data untuk Chart.js
    for item in expense_by_category:
        categories.append({
            'name': item['category__name'] or 'Tanpa Kategori',
            'value': float(item['total']),
            'color': item['category__color'] or '#37a749'
        })
    
    return categories