# core/admin.py
from django.contrib import admin
from django.utils.html import mark_safe
from .models import (
    Skill,
    Category,
    Project,
    BlogPost,
    ContactMessage,
    BlogCategory,
    BlogImage,
    AllResearch,
    DocumentsProjects,
)
# Register your models here.

class BlogImageInline(admin.TabularInline):
    model = BlogImage
    extra = 1
    fields = ['image','alt_text','caption','order']
    ordering = ['order']

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'skill_type', 'proficiency',  'is_featured','order']
    list_filter = ['skill_type', 'is_featured']
    search_fields = ['name']
    list_editable = ['proficiency','is_featured', 'order']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'is_featured', 'created_at']
    list_filter = ['status','category', 'is_featured']
    search_fields = ['title', 'short_description']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['skills_used']
    list_editable = ['is_featured']
    
    fieldsets = (
        ('Basic Information', {
            'fields':('title', 'slug', 'short_description', 'full_description')
        }),
        (
            'Classification',{
                'fields':('category', 'status', 'skills_used','type_project','research_category')
            }
        ),
        (
            'Links & Media', {
                'fields':('thumbnail', 'github_url', 'live_url')
            }
        ),
        (
            'Settiings', {
                'fields':('is_featured', 'order')
            }
        )
    )
    
    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return mark_safe(f'<img src="{obj.thumbnail.url}" width="50" height="50" style="object-fit: cover;"/>')
        return "No Image"
    thumbnail_preview.short_description = 'Preview'
    
    

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    inlines = [BlogImageInline]
    list_display = ['title','category', 'status', 'author', 'created_at', 'is_featured', 'content_type'] 
    list_filter = ['status','category', 'is_featured', 'content_type']  # Add content_type
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    list_editable = ['status','is_featured']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'content_type'),  # Add content_type
            'description': '<a href="/admin/markdown-help/" target="_blank">📖 Panduan Markdown & Math</a>'
        }),
        ('Metadata', {
            'fields': ('category', 'status', 'author', 'published_at', 'is_featured')
        }),
    )
    
    def save_model(self,request, obj, form, change):
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read','created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['name', 'email', 'subject', 'message', 'created_at']
    date_hierarchy = 'created_at'
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f'{queryset.count()} messages marked as read.')
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f'{queryset.count()} messages marked as unread.')  
    
    mark_as_read.short_description = 'Mark selected messages as read'
    mark_as_unread.short_description = 'Mark selected messages as unread'
    
@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
@admin.register(BlogImage)
class BlogImageAdmin(admin.ModelAdmin):
    list_display = ['blog_post', 'alt_text', 'order', 'image_preview']
    list_filter = ['blog_post']
    list_editable = ['order']
    
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" style="object-fit: cover; border-radius: 4px;"/>')
        return "No Image"
    image_preview.short_description = 'Preview'


@admin.register(AllResearch)
class AllResearchAdmin(admin.ModelAdmin):
    list_display = ['kategori', 'astro_research']
    list_filter = ['kategori']
    search_fields = ['kategori']
    
    fieldsets = (
        ('Basic Information', {
            'fields':('kategori', 'astro_research')
        }),
    )

@admin.register(DocumentsProjects)
class DocumentsProjectsAdmin(admin.ModelAdmin):
    list_display = ['projects', 'file_doc','title']
    list_filter = ['projects','title']
    search_fields = ['projects','title']
    
    fieldsets = (
        ('Basic Information', {
            'fields':('projects', 'file_doc','title')
        }),
    )