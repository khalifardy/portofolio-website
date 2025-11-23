# workspace/models/__init__.py

from .pomodoro import (
    PomodoroSettings,
    PomodoroSession,
    DailyPomodoroStats,
)

from .task import (
    TaskList,
    Task,
    TaskComment,
)

from .note import (
    Notebook,
    Note,
    NoteVersion,
)

from .file import (
    FileFolder,
    ResearchFile,
)

from .focus import (
    ResourceLink,
    WorkspacePreferences,
)

# Untuk signals (auto-create settings untuk user baru)
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


@receiver(post_save, sender=User)
def create_user_workspace_settings(sender, instance, created, **kwargs):
    """Auto-create workspace settings for new users"""
    if created:
        PomodoroSettings.objects.get_or_create(user=instance)
        WorkspacePreferences.objects.get_or_create(user=instance)
        
        # Create default task list
        TaskList.objects.get_or_create(
            user=instance,
            is_default=True,
            defaults={'name': 'Inbox', 'icon': '📥'}
        )
        
        # Create default notebook
        Notebook.objects.get_or_create(
            user=instance,
            is_default=True,
            defaults={'name': 'Quick Notes', 'icon': '📓'}
        )