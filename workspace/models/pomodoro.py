from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from research.models import ResearchProject
from .task import Task
import os

class PomodoroSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pomodoro_settings')
    work_duration = models.IntegerField(default=25, validators=[MinValueValidator(1), MaxValueValidator(120)], help_text="work session duration in minutes")
    short_break = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(30)], help_text="short break duration in minutes")
    long_break = models.IntegerField(default=15, validators=[MinValueValidator(5), MaxValueValidator(60)], help_text="long break duration in minutes")
    sessions_before_long_break = models.IntegerField(default=4, validators=[MinValueValidator(2), MaxValueValidator(10)], help_text="number of pomodoros before long break")
    auto_start_breaks = models.BooleanField(default=False, help_text="Automatically start breaks after work session")
    auto_start_pomodoros = models.BooleanField(default=False, help_text="Automatically start next pomodoro after breaks")
    
    SOUND_CHOICES = [
        ('bell', '🔔 Bell'),
        ('chime', '🎵 Chime'),
        ('birds', '🐦 Birds'),
        ('none', '🔇 None'),
    ]
    
    notification_sound = models.CharField(max_length=20, choices=SOUND_CHOICES, default='bell')
    browser_notification = models.BooleanField(default=True)
    
    #Daily goal
    daily_pomodoro_goal = models.IntegerField(default=8, validators=[MinValueValidator(1), MaxValueValidator(20)], help_text="Daily pomodoro goal")
    
    
    class Meta:
        verbose_name = 'Pomodoro Settings'
        verbose_name_plural = 'Pomodoro Settings'
    
    def __str__(self):
        return f"Pomodoro Settings for {self.user.username}"
    
class PomodoroSession(models.Model):
    SESSION_TYPES = [
        ('work', '🍅 Work'),
        ('short_break', '☕ Short Break'),
        ('long_break', '🌴 Long Break'),
    ]
    
    STATUS_CHOICES = [
        ('running', '▶️ Running'),
        ('paused', '⏸️ Paused'),
        ('completed', '✅ Completed'),
        ('cancelled', '❌ Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name='pomodoro_sessions')
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    
    started_at = models.DateTimeField(auto_now_add=True)
    paused_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    planned_duration = models.IntegerField(help_text="Planned duration in seconds")
    actual_duration = models.IntegerField(null=True, blank=True, help_text="Actual duration in seconds")
    
    time_remaining = models.IntegerField(null=True, blank=True, help_text="Time remaining when paused in seconds")
    
    
    task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.SET_NULL, related_name='pomodoro_sessions')
    project = models.ForeignKey(ResearchProject,null=True,blank=True,on_delete=models.SET_NULL, related_name='pomodoro_sessions')
    
    notes =models.TextField(blank=True, help_text="Notes about this session")
    interruptions = models.IntegerField(default=0)
    session_number = models.IntegerField(
        default=1,
        help_text="Which pomodoro in the current cycle (1-4)"
    )
    class Meta:
        ordering = ['-started_at']
        verbose_name = "Pomodoro Session"
        verbose_name_plural = "Pomodoro Sessions"
    
    def __str__(self):
        return f"{self.get_session_type_display()} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"
    
    def complete(self):
        self.status = 'complete'
        self.ended_at = timezone.now()
        if self.started_at:
            delta = self.ended_at - self.started_at
            self.actual_duration = int(delta.total_seconds())
        self.save()
        
        if self.task and self.session_type == 'work':
            self.task.actual_pomodoros += 1
            self.task.save()
    
    def pause(self):
        if self.status =='runnning':
            self.status = 'paused'
            self.paused_at = timezone.now()
            elapsed = (self.paused_at - self.started_at).total_seconds()
            self.time_remaining = max(0,self.planned_duration - int(elapsed))
            self.save()
    
    def resume(self):
        if self.status =='paused' and self.time_remaining:
            self.status = 'running'
            self.started_at = timezone.now() - timezone.timedelta(
                seconds=(self.planned_duration - self.time_remaining)
            )
            self.paused_at = None
            self.save()
    
    def cancel(self):
        self.status = 'cancelled'
        self.ended_at = timezone.now()
        if self.started_at:
            delta = self.ended_at - self.started_at
            self.actual_duration = int(delta.total_seconds())
        self.save()


class DailyPomodoroStats(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_pomodor_stats')
    date = models.DateField()
    
    total_pomodoros = models.IntegerField(default=0)
    complete_pomodoros = models.IntegerField(default=0)
    cancelled_pomodoros = models.IntegerField(default=0)
    total_focus_minutes = models.IntegerField(default=0)
    total_break_minutes = models.IntegerField(default=0)
    total_interuptions = models.IntegerField(default=0)
    
    goal_met = models.BooleanField(default=False)
    class Meta:
        ordering = ['user','date']
        ordering = ['-date']
        verbose_name = 'Daily Pomodoro Stats'
        verbose_name_plural = "Daily Pomodoro Stats"
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"
    
    @classmethod
    def update_for_session(cls,session):
        stats, created = cls.objects.get_or_create(
            user=session.user,
            date=session.started_at.date()
        )
        
        if session.session_type == 'work':
            stats.total_pomodoros += 1
            if session.status == 'completed':
                stats.complete_pomodoros += 1
                stats.total_focus_minutes += (session.actual_duration or 0)//60
            elif session.status == 'completed':
                stats.cancelled_pomodoros += 1
        
        else:
            if session.status =='completed':
                stats.total_break_minutes += (session.actual_duration or 0)//60
        
        stats.total_interuptions += session.interruptions
        
        settings = PomodoroSettings.objects.filter(user=session.user).first()
        if settings:
            stats.goal_met = stats.complete_pomodoros >= settings.daily_pomodoro_goal
        
        stats.save()
        return stats
    