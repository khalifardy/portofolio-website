# finance/admin.py
from django.contrib import admin
from .models import Category, Transaction, Budget, ResearchExpense

# ========================================
# CATEGORY ADMIN
# ========================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'user', 'icon', 'color', 'created_at']
    list_filter = ['type', 'user']
    search_fields = ['name', 'user__username']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'type')
        }),
        ('Display Settings', {
            'fields': ('icon', 'color')
        }),
    )


# ========================================
# TRANSACTION ADMIN
# ========================================

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['description_short', 'type', 'amount_formatted', 'category', 'user', 'date', 'created_at']
    list_filter = ['type', 'date', 'user', 'category']
    search_fields = ['description', 'user__username', 'category__name']
    date_hierarchy = 'date'
    ordering = ['-date', '-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'type', 'amount', 'category')
        }),
        ('Details', {
            'fields': ('description', 'date')
        }),
    )
    
    def description_short(self, obj):
        """Tampilkan deskripsi yang dipotong"""
        if obj.description:
            return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
        return '-'
    description_short.short_description = 'Description'
    
    def amount_formatted(self, obj):
        """Format amount dengan Rupiah"""
        return f"Rp {obj.amount:,.0f}"
    amount_formatted.short_description = 'Amount'
    amount_formatted.admin_order_field = 'amount'


# ========================================
# BUDGET ADMIN
# ========================================

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['category', 'user', 'amount_formatted', 'month', 'spent_display', 'percentage_display']
    list_filter = ['month', 'user', 'category']
    search_fields = ['category__name', 'user__username']
    date_hierarchy = 'month'
    ordering = ['-month']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'category', 'amount', 'month')
        }),
    )
    
    def amount_formatted(self, obj):
        """Format budget amount"""
        return f"Rp {obj.amount:,.0f}"
    amount_formatted.short_description = 'Budget'
    amount_formatted.admin_order_field = 'amount'
    
    def spent_display(self, obj):
        """Tampilkan jumlah yang sudah dipakai"""
        spent = obj.get_spent()
        return f"Rp {spent:,.0f}"
    spent_display.short_description = 'Spent'
    
    def percentage_display(self, obj):
        """Tampilkan persentase penggunaan budget"""
        percentage = obj.get_percentage()
        
        # Color coding based on percentage
        if percentage >= 90:
            color = 'red'
        elif percentage >= 75:
            color = 'orange'
        else:
            color = 'green'
        
        return f'<span style="color: {color}; font-weight: bold;">{percentage:.1f}%</span>'
    percentage_display.short_description = 'Usage %'
    percentage_display.allow_tags = True


# ========================================
# RESEARCH EXPENSE ADMIN
# ========================================

@admin.register(ResearchExpense)
class ResearchExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'field_display', 'amount_formatted', 'user', 'date', 'vendor']
    list_filter = ['field', 'date', 'user']
    search_fields = ['title', 'description', 'vendor', 'user__username']
    date_hierarchy = 'date'
    ordering = ['-date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'field', 'title', 'description')
        }),
        ('Financial Details', {
            'fields': ('amount', 'date')
        }),
        ('Vendor Information', {
            'fields': ('vendor', 'invoice_number')
        }),
    )
    
    def field_display(self, obj):
        """Tampilkan field dengan emoji"""
        field_emoji = {
            'ai': '🤖',
            'physics': '⚛️',
            'math': '📐',
            'engineering': '⚙️',
            'astronomy': '🌌',
        }
        emoji = field_emoji.get(obj.field, '📚')
        return f"{emoji} {obj.get_field_display()}"
    field_display.short_description = 'Field'
    
    def amount_formatted(self, obj):
        """Format amount dengan Rupiah"""
        return f"Rp {obj.amount:,.0f}"
    amount_formatted.short_description = 'Amount'
    amount_formatted.admin_order_field = 'amount'