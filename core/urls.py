# core/urls.py
from django.urls import include, path, re_path
from .views import (
    home,
    project_list,
    project_detail,
    blog_list,
    blog_detail,
    contact,
    about,
    login_view,
    logout_view,
    dashboard_selection
)

app_name = 'core'

urlpatterns = [
    path('', home, name='home'),
    path('about/',about, name='about'),
    path('projects/', project_list, name='projects'),
    path('projects/<slug:slug>/', project_detail, name='project_detail'),
    path('blog/', blog_list, name='blog'),
    path('blog/<slug:slug>/', blog_detail, name='blog_detail'),
    path('contact/', contact, name='contact'),
     # ========================================
    # AUTHENTICATION URLs
    # ========================================
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_selection, name='dashboard'),
]
