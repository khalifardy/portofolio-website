from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from research.models import ResearchProject
from .pomodoro import PomodoroSettings
from .task import TaskList
from .note import Note,Notebook
import os

class ResourceLink(models.Model):
    """External links and references"""
    
    LINK_TYPES = [
        ('paper', '📄 Paper/Article'),
        ('arxiv', '📜 arXiv'),
        ('github', '💻 GitHub'),
        ('dataset', '📊 Dataset'),
        ('tool', '🛠️ Tool'),
        ('tutorial', '📚 Tutorial'),
        ('documentation', '📖 Documentation'),
        ('video', '🎥 Video'),
        ('course', '🎓 Course'),
        ('website', '🌐 Website'),
        ('other', '🔗 Other'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="resource_links",
    )
    
    title = models.CharField(max_length=200)
    url = models.URLField()
    link_type = models.CharField(
        max_length=20,
        choices=LINK_TYPES,
        default='website'
        
    )
    
    description = models.TextField(blank=True)
    
    authors =models.CharField(max_length=500, blank=True)
    publication_year = models.IntegerField(blank=True, null=True)
    journal = models.CharField(max_length=200, blank=True)
    
    project = models.ForeignKey(
        ResearchProject,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='resource_links',
    )
    
    related_notes = models.ManyToManyField(
        Note,
        blank=True,
        related_name='resource_links',
    )
    
    tags = models.JSONField(default=list, blank=True)
    is_favorite = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_favorite', '-created_at']
        verbose_name = 'Resource Link'
        verbose_name_plural = 'Resource Links'
        
    def __str__(self):
        return self.title


class WorkspacePreferences(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="workspace_preference",
    )
    
    THEME_CHOICES = [
        ('dark', '🌙 Dark'),
        ('light', '☀️ Light'),
        ('auto', '🔄 Auto'),
    ]
    
    theme = models.CharField(
        max_length=10,
        choices=THEME_CHOICES,
        default='dark',
    )
    
    sidebar_collapsed = models.BooleanField(default=False)
    default_view = models.CharField(
        max_length=20,
        default='dashboard',
        help_text='Default view: dashboard, projects, tasks, notes, files, or settings'
    )
    
    show_pomodoro_widget = models.BooleanField(default=True)
    show_tasks_widget = models.BooleanField(default=True)
    show_calendar_widget = models.BooleanField(default=True)
    show_stats_widget = models.BooleanField(default=True)
    show_recent_notes_widget = models.BooleanField(default=True)
    
    
    default_task_list_id = models.IntegerField(null=True, blank=True)
    hide_completed_tasks = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Workspace Preference'
        verbose_name_plural = 'Workspace Preferences'
    
    def __str__(self):
        return f"Workspace Preference for {self.user.username}"
    
