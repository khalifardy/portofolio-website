# research/urls.py
from django.urls import path
from .views import (research_dashboard,astronomy_research_detail,
                    astronomy_research_list,project_create,
                    project_edit, project_delete, project_list,
                    project_detail, export_projects_csv)

app_name = 'research'

urlpatterns = [
    # Dashboard
    path('', research_dashboard, name='dashboard_research'),
    path('projects/', project_list, name='project_list'),
    path('projects/create/', project_create, name='project_create'),
    path('projects/export-csv/', export_projects_csv, name='export_csv'),
    path('projects/<slug:slug>/edit/', project_edit, name='project_edit'),
    path('projects/<slug:slug>/delete/', project_delete, name='project_delete'),
    path('projects/<slug:slug>/', project_detail, name='project_detail'),
    
    # Astronomy Research Integration
    path('astronomy/', astronomy_research_list, name='astronomy_list'),
    path('astronomy/<slug:slug>/', astronomy_research_detail, name='astronomy_detail'),
]