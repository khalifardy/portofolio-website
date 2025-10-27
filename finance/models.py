# finance/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    """Kategori untuk transaksi"""
    CATEGORY_TYPES = (
        ('income', 'Pemasukan'),
        ('expense', 'Pengeluaran'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    icon = models.CharField(max_length=50, default='💰')
    color = models.CharField(max_length=7, default='#37a749')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Transaction(models.Model):
    """Model untuk transaksi keuangan"""
    TRANSACTION_TYPES = (
        ('income', 'Pemasukan'),
        ('expense', 'Pengeluaran'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.TextField(blank=True)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.get_type_display()} - Rp {self.amount:,.0f} ({self.date})"


class Budget(models.Model):
    """Model untuk budget bulanan per kategori"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    month = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'category', 'month']
        ordering = ['-month']
    
    def __str__(self):
        return f"Budget {self.category.name} - {self.month.strftime('%B %Y')}"
    
    def get_spent(self):
        """Hitung total pengeluaran untuk kategori ini di bulan ini"""
        return Transaction.objects.filter(
            user=self.user,
            category=self.category,
            type='expense',
            date__year=self.month.year,
            date__month=self.month.month
        ).aggregate(models.Sum('amount'))['amount__sum'] or 0
    
    def get_percentage(self):
        """Hitung persentase penggunaan budget"""
        spent = self.get_spent()
        if self.amount > 0:
            return (spent / self.amount) * 100
        return 0


class ResearchExpense(models.Model):
    """Model untuk pengeluaran riset"""
    RESEARCH_FIELDS = (
        ('ai', 'AI & Machine Learning'),
        ('physics', 'Fisika'),
        ('math', 'Matematika'),
        ('engineering', 'Engineering'),
        ('astronomy', 'Astronomi'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    field = models.CharField(max_length=20, choices=RESEARCH_FIELDS)
    title = models.CharField(max_length=200)
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=timezone.now)
    vendor = models.CharField(max_length=200, blank=True)
    invoice_number = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.get_field_display()} - {self.title}"
#