from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from research.models import ResearchProject
from .task import Task
import os

class Notebook(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notebooks",
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(
        max_length=7,
        default='#37a749'
    )
    icon = models.CharField(
        max_length=10,
        default='📓'
        
    )
    
    project = models.ForeignKey(
        ResearchProject,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='notebooks',
    )
    
    is_default =models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Notebook'
        verbose_name_plural = 'Notebooks'
    
    
    def __str__(self):
        return self.name
    
    def get_notes_count(self):
        return self.notes.count()
    
    
class Note(models.Model):
    """Individual notes with Markdown support"""
    
    NOTE_TYPES = [
        ('note', '📝 Note'),
        ('meeting', '🤝 Meeting Notes'),
        ('idea', '💡 Idea'),
        ('reference', '📚 Reference'),
        ('log', '📋 Log Entry'),
        ('snippet', '💻 Code Snippet'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notes",
    )
    
    notebook = models.ForeignKey(
        Notebook,
        on_delete=models.CASCADE,
        related_name="notes",
    )
    
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Markdown supported")
    note_type = models.CharField(
        max_length=20,
        choices=NOTE_TYPES,
        default='note',
    )
    
    project = models.ForeignKey(
        ResearchProject,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='notes',
    )
    
    related_tasks = models.ManyToManyField(
        Task,
        blank=True,
        related_name='related_notes'
    )
    
    tags = models.JSONField(default=list, blank=True)
    is_pinned = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_favorite = models.BooleanField(default=False)
    
    word_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_pinned', '-updated_at']
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.word_count = len(self.content.split())
        
        if self.pk:
            try:
                old_note = Note.objects.get(pk=self.pk)
                if old_note.content != self.content:
                    NoteVersion.objects.create(
                        note=self,
                        content=old_note.content
                    )
            except Note.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)

class NoteVersion(models.Model):
    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name="versions",
    )
    
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Version {self.note.title} of {self.created_at}"