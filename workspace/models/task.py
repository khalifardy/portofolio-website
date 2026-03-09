from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from research.models import ResearchProject
import os


class TaskList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="task_lists",
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(
        max_length=7,
        default='#37a749',
        help_text='Hex color code (e.g., #37a749)',
    )
    icon = models.CharField(max_length=10, default='📋')
    project = models.ForeignKey(
        
        ResearchProject,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='task_lists',
        
    )
    
    position = models.IntegerField(default=0)
    is_default = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position', 'name']
        verbose_name = 'Task List'
        verbose_name_plural = 'Task Lists'
    
    def __str__(self):
        return f"{self.icon} {self.name}"
    
    def get_open_tasks_count(self):
        return self.tasks.exclude(status__in=['completed', 'cancelled']).count()
    
    def get_completed_tasks_count(self):
        return self.tasks.filter(status='completed').count()

class Task(models.Model):
    """Individual tasks with full tracking"""
    
    PRIORITY_CHOICES = [
        (1, '🔴 Urgent'),
        (2, '🟠 High'),
        (3, '🟡 Medium'),
        (4, '🟢 Low'),
    ]
    
    STATUS_CHOICES = [
        ('todo', '📋 To Do'),
        ('in_progress', '🔄 In Progress'),
        ('blocked', '🚫 Blocked'),
        ('review', '👀 In Review'),
        ('done', '✅ Done'),
        ('cancelled', '❌ Cancelled'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    
    task_list = models.ForeignKey(
        TaskList,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='todo',
    )
    
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=3,
    )
    
    due_date = models.DateTimeField(null=True, blank=True)
    reminder_date = models.DateTimeField(null=True, blank=True)
    estimated_pomodoros = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    
    actual_pomodoros = models.IntegerField(default=0)
    
    RECURRENCE_CHOICES = [
        ('none', 'None'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    recurrence = models.CharField(
        max_length=20,
        choices=RECURRENCE_CHOICES,
        default='none',
    )
    
    project = models.ForeignKey(
        ResearchProject,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='tasks',
    )
    
    parent_task = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='subtasks',
    )
    
    tags = models.JSONField(default=list, blank=True)
    
    position = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['status','priority','position','-created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
    
    def __str__(self):
        return self.title
    
    def complete(self):
        self.status = 'done'
        self.completed_at = timezone.now()
        self.save()
    
    def reopen(self):
        self.status = 'todo'
        self.completed_at = None
        self.save()
    
    def is_overdue(self):
        if self.due_date and self.status not in ['done', 'cancelled']:
            return timezone.now() > self.due_date
        return False
    
    def get_progress_percentage(self):
        if self.estimated_pomodoros > 0:
            return int(100, int((self.actual_pomodoros/self.estimated_pomodoros)*100))
        return 0
    
    def get_subtasks_count(self):
        return self.subtasks.count()
    
    def get_completed_subtasks_count(self):
        return self.subtasks.filter(status='done').count()
    
class TaskComment(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    
    content = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Comment on {self.task.title} by {self.user.username}"