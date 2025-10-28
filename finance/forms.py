# finance/forms.py
from django import forms
from .models import Transaction, Category
from django.utils import timezone

class TransactionForm(forms.ModelForm):
    """Form untuk create/edit transaksi"""
    
    def __init__(self, *args, **kwargs):
        # Ambil user dari kwargs
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter kategori berdasarkan user yang login
        if self.user:
            self.fields['category'].queryset = Category.objects.filter(user=self.user)
        
        # Custom attributes untuk styling
        self.fields['type'].widget.attrs.update({
            'class': 'type-radio',
        })
        
        self.fields['amount'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': '0',
            'min': '0',
            'step': '1',
            'id': 'amount',
        })
        
        self.fields['category'].widget.attrs.update({
            'class': 'form-select',
            'id': 'category',
        })
        
        self.fields['date'].widget.attrs.update({
            'class': 'form-input',
            'type': 'date',
            'id': 'date',
        })
        
        self.fields['description'].widget.attrs.update({
            'class': 'form-textarea',
            'placeholder': 'Catatan tambahan...',
            'id': 'description',
            'rows': 4,
        })
        
        # Set default date to today if creating new transaction
        if not self.instance.pk:
            self.fields['date'].initial = timezone.now().date()
    
    class Meta:
        model = Transaction
        fields = ['type', 'amount', 'category', 'date', 'description']
        
        widgets = {
            'type': forms.RadioSelect(
                choices=Transaction.TRANSACTION_TYPES,
                attrs={'class': 'type-radio'}
            ),
            'amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0',
                'min': '0',
                'step': '1',
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
            }),
        }
        
        labels = {
            'type': '💱 Tipe Transaksi',
            'amount': '💰 Jumlah (Rp)',
            'category': '📂 Kategori',
            'date': '📅 Tanggal',
            'description': '📝 Deskripsi',
        }
    
    def clean_amount(self):
        """Validasi amount harus lebih dari 0"""
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError('Jumlah harus lebih dari 0!')
        return amount
    
    def clean_category(self):
        """Validasi kategori harus dipilih"""
        category = self.cleaned_data.get('category')
        if not category:
            raise forms.ValidationError('Kategori harus dipilih!')
        return category