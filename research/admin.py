# research/admin.py
from django.contrib import admin
from .models import ResearchProject

@admin.register(ResearchProject)
class ResearchProjectAdmin(admin.ModelAdmin):
    list_display = [
        'title', 
        'field', 
        'status', 
        'priority', 
        'progress_percentage', 
        'user', 
        'start_date',
        'created_at'
    ]
    list_filter = ['field', 'status', 'priority', 'is_public', 'is_published']
    search_fields = ['title', 'description', 'objectives', 'user__username']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'slug', 'field', 'description')
        }),
        ('Research Details', {
            'fields': ('objectives', 'methodology', 'hypothesis')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date')
        }),
        ('Status & Progress', {
            'fields': ('status', 'priority', 'progress_percentage')
        }),
        ('Results', {
            'fields': ('findings', 'conclusions', 'future_work'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('institution', 'supervisor', 'collaborators'),
            'classes': ('collapse',)
        }),
        ('Flexible Data', {
            'fields': ('data_schema',),
            'classes': ('collapse',),
            'description': 'JSON field untuk data spesifik per bidang riset'
        }),
        ('Configuration', {
            'fields': ('is_public', 'is_published'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)