from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from research.models import ResearchProject
from .task import Task
from .note import Note
import os

class FileFolder(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="file_folders",
    )
    
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='subfolders',
    )
    
    project = models.ForeignKey(
        ResearchProject,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='file_folders',
    )
    
    icon = models.CharField(max_length=10, default='📂')
    color = models.CharField(max_length=7, default='#37a749')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering =['name']
        verbose_name ='File Folders'
        verbose_name_plural = 'File Folders'
        
    def __str__(self):
        return self.get_full_path()
    
    def get_full_path(self):
        path  =  [self.name]
        parent = self.parent
        
        while parent:
            path.insert(0,parent.name)
            parent = parent.parent
        
        return '/' + '/'.join(path) + '/'
    
    def get_files_count(self):
        return self.files.count()
    
    def get_total_size(self):
        return self.files.aggregate(
            total=models.Sum('file_size')
        )['total'] or 0
        
def research_file_path(instance,filename):
    project_id = instance.project.id if instance.project else 'general'
    return f'workspace/files/{instance.user.id}/{project_id}/{filename}'

class ResearchFile(models.Model):
    """Files associated with research/projects"""
    
    FILE_TYPES = [
        ('data', '📊 Data'),
        ('code', '💻 Code'),
        ('document', '📄 Document'),
        ('image', '🖼️ Image'),
        ('reference', '📚 Reference/Paper'),
        ('output', '📈 Output/Result'),
        ('presentation', '📽️ Presentation'),
        ('other', '📎 Other'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="research_files",
    )
    
    folder = models.ForeignKey(
        FileFolder,
        on_delete=models.SET_NULL,
        related_name="files",
        null=True,
        blank=True,
    )
    
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to=research_file_path)
    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPES,
        default='other',
    )
    
    description = models.TextField(blank=True)
    
    project = models.ForeignKey(
        ResearchProject,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='research_files',
    )
    
    related_notes = models.ManyToManyField(
        Note,
        blank=True,
        related_name='attached_files',
    )
    
    file_size = models.BigIntegerField(default=0, help_text="Size in bytes")
    mime_type = models.CharField(max_length=100, blank=True)
    original_filename = models.CharField(max_length=255, blank=True)
    
    tags = models.JSONField(default=list, blank=True)
    is_favorite = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Research File'
        verbose_name_plural = 'Research Files'
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
            if not self.original_filename:
                self.original_filename = os.path.basename(self.file.name)
        super().save(*args, **kwargs)
        
    def get_file_size_display(self):
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def get_extension(self):
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()

