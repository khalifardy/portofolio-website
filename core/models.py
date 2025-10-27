# core/models.py
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from astronomy.models import ResearchProject as astronomy_research

# Create your models here.

#all Research
class AllResearch(models.Model):
    KATEGORI_RESEARCH = [
        ('Astronomy', 'Astronomy'),
        ("AI & Machine Learning", "AI & Machine Learning"),
        ("Physics", "Physics"),
        ("Engineering", "Engineering"),
        ("Mathematics", "Mathematics"),
        ("Other", "Other")
    ]
    astro_research = models.ForeignKey(astronomy_research, on_delete=models.CASCADE,null=True,blank=True)
    kategori = models.CharField(max_length=100, choices=KATEGORI_RESEARCH)
    
    def __str__(self):
        return self.astro_research.title

#Skill Model
class Skill(models.Model):
    """Skills dan Technologies"""
    
    SKILL_TYPES = [
        ('language', 'Programming Language'),
        ('framework', 'Framework/Library'),
        ('tool', 'Tool/Software'),
        ('concept', 'Concept/Theory')
    ]
    
    name = models.CharField(max_length=100)
    skill_type = models.CharField(max_length=20, choices=SKILL_TYPES)
    icon = models.CharField(max_length=100, blank=True, help_text="Emoji atau icon class")
    image_icon = models.ImageField(upload_to='skills/', blank=True, null=True)
    proficiency = models.IntegerField(default=80, help_text="Proficiency level 0-100")
    order = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['order','name']
    
    def __str__(self):
        return self.name

#Category Model
class Category(models.Model):
    """Kategori untuk projects"""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
# Category untuk Blog
class BlogCategory(models.Model):
    """Kategori khusus untuk blog posts"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categories"
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
#Project Model
class Project(models.Model):
    """Portofolio Projects"""
    
    PROJECT_STATUS = [
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('planned', 'Planned')
    ]
    
    TYPE_PROJECT = [
        ('projects','Projects'),
        ('research','Research')
    ]
    
    #Basic Info
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    short_description = models.CharField(max_length=300)
    full_description = models.TextField()
    
    #Classification
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='projects')
    status = models.CharField(max_length=20, choices=PROJECT_STATUS, default='in_progress')
    skills_used = models.ManyToManyField(Skill, related_name='projects',blank=True)
    
    #Links
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    
    # IMAGES
    thumbnail = models.ImageField(upload_to='projects/thumbnails/',blank=True,null=True)
    
    type_project = models.CharField(max_length=20, choices=TYPE_PROJECT, default='projects')
    research_category = models.ForeignKey(AllResearch,on_delete=models.SET_NULL,null=True, blank=True)
    
    #Metadata
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-is_featured', 'order', '-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    
    def __str__(self):
        return self.title
    
#BlogPost Model (simple version for now)

class BlogPost(models.Model):
    """Blog Posts"""
    
    POST_STATUS = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    CONTENT_TYPE = [
        ('html', 'HTML'),
        ('markdown', 'Markdown')
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    excerpt = models.TextField(max_length=500, help_text="Short preview")
    content = models.TextField()
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE, default='markdown')
    
    status = models.CharField(max_length=20, choices=POST_STATUS, default='draft')
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, related_name='blog_posts')
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    is_featured = models.BooleanField(default=False)
    
    reading_time_minutes = models.PositiveIntegerField(default=5)
    
    class Meta:
        ordering = ['-published_at', '-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
    
        # Auto-calculate reading time
        if self.content:
            word_count = len(self.content.split())
            self.reading_time_minutes = max(1, word_count // 200)
    
        # Set published_at when changing to published
        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
    
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title


class BlogImage(models.Model):
    """image for blog posts"""
    
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='blog_images/')
    caption = models.CharField(max_length=500, blank=True)
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.blog_post.title}"
    
#Contact Message Model
class ContactMessage(models.Model):
    """Contact form Messages"""
    
    name =models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subject} - {self.name}"
       
    
class DocumentsProjects(models.Model):
    file_doc = models.FileField(upload_to='documents/', blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    projects = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    
    def __str__(self):
        return f"{self.projects.title} - {self.title}"
    