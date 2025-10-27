# research/models.py
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class ResearchProject(models.Model):
    """
    General Research Project untuk berbagai bidang riset
    Menggunakan JSON field untuk fleksibilitas data per bidang
    """
    
    RESEARCH_FIELDS = [
        ('ai', 'AI & Machine Learning'),
        ('physics', 'Physics'),
        ('mathematics', 'Mathematics'),
        ('engineering', 'Engineering'),
        ('astronomy', 'Astronomy'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Basic Info
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='research_projects')
    title = models.CharField(max_length=200, help_text="Judul penelitian")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    field = models.CharField(max_length=20, choices=RESEARCH_FIELDS, help_text="Bidang penelitian")
    description = models.TextField(help_text="Deskripsi singkat penelitian")
    
    # Research Details
    objectives = models.TextField(help_text="Tujuan penelitian")
    methodology = models.TextField(blank=True, help_text="Metode yang digunakan")
    hypothesis = models.TextField(blank=True, help_text="Hipotesis (jika ada)")
    
    # Timeline
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    
    # Status & Priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    progress_percentage = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Progress dalam persentase (0-100)"
    )
    
    # Results
    findings = models.TextField(blank=True, help_text="Temuan/hasil penelitian")
    conclusions = models.TextField(blank=True, help_text="Kesimpulan")
    future_work = models.TextField(blank=True, help_text="Rencana pengembangan selanjutnya")
    
    # Flexible Data Schema (JSON) - untuk data spesifik per bidang
    data_schema = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Data fleksibel dalam format JSON untuk kebutuhan spesifik per bidang"
    )
    
    # Metadata
    institution = models.CharField(max_length=200, blank=True, help_text="Institusi/organisasi")
    supervisor = models.CharField(max_length=200, blank=True, help_text="Supervisor/pembimbing")
    collaborators = models.TextField(blank=True, help_text="Kolaborator/tim (satu per baris)")
    
    # Configuration
    is_public = models.BooleanField(default=False, help_text="Apakah riset ini public?")
    is_published = models.BooleanField(default=False, help_text="Sudah dipublikasikan?")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at', '-created_at']
        verbose_name = 'Research Project'
        verbose_name_plural = 'Research Projects'
        indexes = [
            models.Index(fields=['field', 'status']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} ({self.get_field_display()})"
    
    def get_duration_days(self):
        """Hitung durasi penelitian dalam hari"""
        if self.end_date:
            return (self.end_date - self.start_date).days
        return (timezone.now().date() - self.start_date).days
    
    def get_status_badge_color(self):
        """Return warna badge berdasarkan status"""
        colors = {
            'planning': '#6c757d',  # gray
            'active': '#37a749',    # green
            'paused': '#ffc107',    # yellow
            'completed': '#0d6efd', # blue
            'archived': '#6c757d',  # gray
        }
        return colors.get(self.status, '#6c757d')
    
    def get_priority_badge_color(self):
        """Return warna badge berdasarkan priority"""
        colors = {
            'low': '#6c757d',      # gray
            'medium': '#0d6efd',   # blue
            'high': '#ffc107',     # yellow
            'urgent': '#dc3545',   # red
        }
        return colors.get(self.priority, '#6c757d')