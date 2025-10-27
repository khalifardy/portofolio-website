# research/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import ResearchProject
from .forms import ResearchProjectForm
from astronomy.models import (
    ResearchProject as AstroResearchProject,
    ResearchDataEntry,
    ResearchAnalysis,
    ObservationLog,
    AstroPhoto
)



@login_required
def research_dashboard(request):
    """
    Main dashboard untuk research management
    Menampilkan statistik dan list projects
    """
    
    # Get general research projects
    general_projects = ResearchProject.objects.filter(user=request.user)
    
    # Get astronomy research projects (untuk integrasi)
    astro_projects = AstroResearchProject.objects.all()
    
    # Statistics
    total_projects = general_projects.count() + astro_projects.count()
    active_projects = general_projects.filter(status='active').count() + \
                      astro_projects.filter(status='active').count()
    completed_projects = general_projects.filter(status='completed').count() + \
                         astro_projects.filter(status='completed').count()
    planning_projects = general_projects.filter(status='planning').count() + \
                        astro_projects.filter(status='planning').count()
    
    # Projects by field
    projects_by_field = general_projects.values('field').annotate(
        count=Count('id')
    ).order_by('-count')
    
    projects_by_status = general_projects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Recent projects (last 5)
    recent_general = general_projects.order_by('-updated_at')[:5]
    recent_astro = astro_projects.order_by('-updated_at')[:3]
    
    # High priority projects
    high_priority = general_projects.filter(
        priority__in=['high', 'urgent'],
        status__in=['active', 'planning']
    ).order_by('-priority', '-updated_at')[:5]
    
    # Calculate average progress for active projects
    active_general = general_projects.filter(status='active')
    avg_progress = 0
    if active_general.exists():
        total_progress = sum([p.progress_percentage for p in active_general])
        avg_progress = total_progress / active_general.count()
    
    field_labels = []
    field_data = []
    field_colors = {
        'ai': '#667eea',
        'physics': '#f093fb',
        'mathematics': '#4facfe',
        'engineering': '#fa709a',
        'astronomy': '#feca57',
        'other': '#6c757d',
    }
    field_chart_colors = []
    
    for item in projects_by_field:
        field_display = dict(ResearchProject.RESEARCH_FIELDS).get(item['field'], item['field'])
        field_labels.append(field_display)
        field_data.append(item['count'])
        field_chart_colors.append(field_colors.get(item['field'], '#6c757d'))
    
    status_labels = []
    status_data = []
    for item in projects_by_status:
        status_display = dict(ResearchProject.STATUS_CHOICES).get(item['status'], item['status'])
        status_labels.append(status_display)
        status_data.append(item['count'])
        
    
    context = {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'planning_projects': planning_projects,
        'projects_by_field': projects_by_field,
        'recent_general': recent_general,
        'recent_astro': recent_astro,
        'high_priority': high_priority,
        'avg_progress': round(avg_progress, 1),
        # Chart data (convert to JSON for JavaScript)
        'field_labels': json.dumps(field_labels),
        'field_data': json.dumps(field_data),
        'field_colors': json.dumps(field_chart_colors),
        'status_labels': json.dumps(status_labels),
        'status_data': json.dumps(status_data),
    }
    
    return render(request, 'research/dashboard_research.html', context)


@login_required
def astronomy_research_list(request):
    """
    List semua astronomy research projects
    """
    projects = AstroResearchProject.objects.all().order_by('-updated_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        projects = projects.filter(status=status_filter)
    
    # Filter by research type if provided
    type_filter = request.GET.get('type')
    if type_filter:
        projects = projects.filter(research_type=type_filter)
    
    context = {
        'projects': projects,
        'status_filter': status_filter,
        'type_filter': type_filter,
    }
    
    return render(request, 'research/astronomy_list.html', context)


@login_required
def astronomy_research_detail(request, slug):
    """
    Detail astronomy research project dengan semua data
    """
    project = get_object_or_404(AstroResearchProject, slug=slug)
    
    # Get related data
    data_entries = ResearchDataEntry.objects.filter(
        project=project
    ).order_by('-observation_datetime')
    
    analyses = ResearchAnalysis.objects.filter(
        project=project
    ).order_by('-created_at')
    
    observations = ObservationLog.objects.filter(
        research_project=project
    ).order_by('-observation_date')
    
    photos = AstroPhoto.objects.filter(
        research_project=project
    ).order_by('-capture_date')
    
    context = {
        'project': project,
        'data_entries': data_entries,
        'analyses': analyses,
        'observations': observations,
        'photos': photos,
        'data_entries_count': data_entries.count(),
        'analyses_count': analyses.count(),
        'observations_count': observations.count(),
        'photos_count': photos.count(),
    }
    
    return render(request, 'research/astronomy_detail.html', context)


@login_required
def project_create(request):
    """
    Create new general research project
    """
    if request.method == 'POST':
        form = ResearchProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            messages.success(request, f'Research project "{project.title}" has been created successfully!')
            return redirect('research:project_detail', slug=project.slug)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ResearchProjectForm()
    
    context = {
        'form': form,
        'mode': 'create',
    }
    
    return render(request, 'research/project_form.html', context)

@login_required
def project_edit(request, slug):
    """
    Edit existing general research project
    """
    project = get_object_or_404(ResearchProject, slug=slug, user=request.user)
    
    if request.method == 'POST':
        form = ResearchProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            messages.success(request, f'Research project "{project.title}" has been updated successfully!')
            return redirect('research:project_detail', slug=project.slug)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ResearchProjectForm(instance=project)
    
    context = {
        'form': form,
        'mode': 'edit',
        'project': project,
    }
    
    return render(request, 'research/project_form.html', context)


@login_required
def project_delete(request, slug):
    """
    Delete research project
    """
    project = get_object_or_404(ResearchProject, slug=slug, user=request.user)
    
    if request.method == 'POST':
        project_title = project.title
        project.delete()
        messages.success(request, f'Research project "{project_title}" has been deleted successfully!')
        return redirect('research:project_list')
    
    context = {
        'project': project,
    }
    
    return render(request, 'research/project_delete.html', context)

@login_required
def project_list(request):
    """
    List all general research projects with filters
    """
    projects = ResearchProject.objects.filter(user=request.user).order_by('-updated_at')
    
    # Filter by field
    field_filter = request.GET.get('field')
    if field_filter:
        projects = projects.filter(field=field_filter)
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        projects = projects.filter(status=status_filter)
    
    # Filter by priority
    priority_filter = request.GET.get('priority')
    if priority_filter:
        projects = projects.filter(priority=priority_filter)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        projects = projects.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(objectives__icontains=search_query)
        )
    
    # Statistics for this view
    total_count = projects.count()
    active_count = projects.filter(status='active').count()
    completed_count = projects.filter(status='completed').count()
    
    context = {
        'projects': projects,
        'field_filter': field_filter,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'search_query': search_query,
        'total_count': total_count,
        'active_count': active_count,
        'completed_count': completed_count,
    }
    
    return render(request, 'research/project_list.html', context)

@login_required
def project_detail(request, slug):
    """
    Detail page for general research project
    """
    project = get_object_or_404(ResearchProject, slug=slug, user=request.user)
    
    # Calculate duration
    duration_days = project.get_duration_days()
    
    # Parse collaborators (one per line)
    collaborators_list = []
    if project.collaborators:
        collaborators_list = [c.strip() for c in project.collaborators.split('\n') if c.strip()]
    
    context = {
        'project': project,
        'duration_days': duration_days,
        'collaborators_list': collaborators_list,
    }
    
    return render(request, 'research/project_detail.html', context)

@login_required
def export_projects_csv(request):
    """
    Export all user's research projects to CSV
    """
    import csv
    from django.http import HttpResponse
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="research_projects.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Title',
        'Field',
        'Status',
        'Priority',
        'Progress (%)',
        'Start Date',
        'End Date',
        'Institution',
        'Supervisor',
        'Created At',
        'Updated At',
    ])
    
    # Write data
    projects = ResearchProject.objects.filter(user=request.user).order_by('-created_at')
    for project in projects:
        writer.writerow([
            project.title,
            project.get_field_display(),
            project.get_status_display(),
            project.get_priority_display(),
            project.progress_percentage,
            project.start_date.strftime('%Y-%m-%d') if project.start_date else '',
            project.end_date.strftime('%Y-%m-%d') if project.end_date else '',
            project.institution or '',
            project.supervisor or '',
            project.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            project.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])
    
    return response