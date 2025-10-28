# core/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import (
    Project, 
    Skill, 
    BlogPost,
    Category,
    BlogCategory,
    ContactMessage,
    DocumentsProjects,)

from astronomy.models import (
    AstroPhoto,
    )

from .utils import process_markdown, insert_blog_images
def home(request):
    # Get featured projects
    """
    Homepage view. Retrieves featured projects, skills, and latest blog posts
    and passes them to the home.html template for rendering.

    :param request: HttpRequest object
    :return: HttpResponse object
    """

    featured_projects = Project.objects.filter(is_featured=True)[:3]
    
    # Get featured skills
    featured_skills = Skill.objects.filter(is_featured=True)[:6]
    
    # Get latest blog posts (fix: latest_posts dengan 's')
    latest_posts = BlogPost.objects.filter(status='published').order_by('-published_at')[:3]
    
    astro_photos = AstroPhoto.objects.filter(is_featured=True, is_public=True)
    if len(astro_photos)>6:
        astro_photos = astro_photos[:6]
    
    context = {
        'title': 'Home',
        'featured_projects': featured_projects,
        'featured_skills': featured_skills,
        'latest_posts': latest_posts,
        'astro_photos': astro_photos,  # Add this
    }
    
    
    return render(request, 'core/home.html', context)

def project_list(request):
    """
    Display all projects with pagination. The projects are ordered by
    -is_featured (i.e., featured projects first) and -created_at (i.e.,
    newer projects first). The view also supports filtering projects by
    category.

    :param request: HttpRequest object
    :return: HttpResponse object
    """
    #Retrieve all projects
    projects = Project.objects.all().distinct().order_by('-is_featured', '-created_at')
    
    # Filter by type (projects vs research)
    type_filter = request.GET.get('type')
    if type_filter and type_filter != 'all':
        projects = projects.filter(type_project=type_filter)
    
    # Filter projects by category if requested
    category_slug = request.GET.get('category')
    if category_slug:
        projects = projects.filter(category__slug=category_slug)
    
    # Filter by research category if requested
    research_category = request.GET.get('research_category')
    if research_category:
        projects = projects.filter(
            type_project='research',
            research_category__kategori=research_category
        )
    
    # Set up pagination
    paginator = Paginator(projects, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Retrieve categories for the sidebar
    categories = Category.objects.all()
    
    # Set up context
    context = {
        'projects': page_obj,
        'categories': categories,
        'current_category': category_slug,
        'research_category': research_category,
    }
    
    return render(request, 'core/projects.html', context)

def project_detail(request, slug):
    """
    Display the details of a project specified by the slug. The function
    first retrieves the project with the given slug. If the project does not
    exist, it returns a 404 error. The function then gets up to three related
    projects by filtering projects with the same category but excluding the
    current project. The projects are ordered by their created_at field in
    descending order. The function then sets up a context dictionary with the
    project and related projects and renders the HTML template
    project_detail.html with the context.

    :param request: HttpRequest object
    :param slug: slug of the project
    :return: HttpResponse object
    """
    project = get_object_or_404(Project, slug=slug)
    document = DocumentsProjects.objects.filter(projects=project)
    
    
    # Retrieve related projects
    related_projects = Project.objects.filter(
        category=project.category
    ).exclude(id=project.id).order_by('-created_at')[:3]
    
    # Set up context
    context = {
        'project': project,
        'related_projects': related_projects,
        'document': document
    }
    return render(request, 'core/project_detail.html', context)


def blog_list(request):
    """
    Display all published blog post

    The function first retrieves all published blog posts. It then filters the
    posts based on the search query and category filter. The function then
    paginates the posts and sets up a context dictionary with the paginated
    posts, all categories for the sidebar, recent posts, current category and
    search query. Finally, the function renders the HTML template blog.html
    with the context.

    :param request: HttpRequest object
    :return: HttpResponse object
    """
    
    # Retrieve all published blog posts
    posts = BlogPost.objects.filter(status='published').order_by('-published_at', '-created_at')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        # Filter the posts based on the search query
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    
    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        # Filter the posts based on the category filter
        posts = posts.filter(category__slug=category_slug)
    
    # Pagination
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get All categories for sidebar
    categories = BlogCategory.objects.all()
    recent_posts = BlogPost.objects.filter(status='published').order_by('-published_at')[:5]
    
    
    # Set up context
    context = {
        
        'page_obj': page_obj,
        'categories': categories,
        'recent_posts': recent_posts,
        'current_category': category_slug,
        'search_query': search_query
    }
    
    return render(request, 'core/blog.html', context)


def blog_detail(request, slug):
    """
    Display single blog post with markdown processing
    
    :param request: Request object
    :param slug: Slug of the blog post
    :return: Rendered blog post page
    """
    
    # Get the blog post with the given slug
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    
    # Process content based on type
    if post.content_type == 'markdown':
        # Insert images first, then process markdown
        content_with_images = insert_blog_images(post.content, post)
        processed_content = process_markdown(content_with_images)
    else:
        processed_content = post.content
    
    # Get 3 related posts, excluding the current post
    related_posts = BlogPost.objects.filter(
        category=post.category,
        status='published'
        ).exclude(id=post.id)[:3]
    
    # Set up context
    context = {
        'post': post,
        'processed_content': processed_content,  # Add processed content
        'related_posts': related_posts
    }
    
    # Return rendered blog post page
    return render(request, 'core/blog_detail.html', context)

def contact(request):
    """Contact Form Page"""
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
    
        #create contact message
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
    
        messages.success(request, "Your message has been sent !, I will get back to you")
        return redirect('core:contact')
    
    return render(request, 'core/contact.html')


def about(request):
    """About Page"""
    
    context = {
        'page_title':'About Me'
    }
    
    return render(request, 'core/about.html', context)

# ========================================
# AUTHENTICATION VIEWS
# ========================================

def login_view(request):
    """
    View untuk handle login user
    - GET: Tampilkan form login
    - POST: Process login credentials
    """
    # Redirect jika sudah login
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    # Handle POST request (form submission)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login berhasil
            login(request, user)
            messages.success(request, f'Selamat datang kembali, {user.username}!',extra_tags="login")
            return redirect('core:dashboard')
        else:
            # Login gagal
            messages.error(request, 'Username atau password salah!',extra_tags="login")
           
        
        
    
    # Render form login
    return render(request, 'core/login.html')

@login_required
def dashboard_selection(request):
    return render(request, 'core/dashboard_selection.html')

@login_required
def logout_view(request):
    """
    View untuk handle logout user
    """
    logout(request)
    messages.info(request, 'Anda telah logout.',extra_tags="login")
    return redirect('core:login')