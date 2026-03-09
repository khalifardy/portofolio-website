from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.utils import timezone
from django.db.models import Count, Sum, Q, F
from datetime import datetime, timedelta
from django.core.paginator import Paginator
import json

from django.http import JsonResponse

from library_helper.workspace import calculate_streak, get_week_stats

from .models.pomodoro import (
    PomodoroSession, PomodoroSettings, DailyPomodoroStats
)

from .models.task import (
    TaskList, Task, TaskComment
)

from .models.note import (
    Notebook, Note, NoteVersion
)

from .models.file import (
    FileFolder, ResearchFile
)

from .models.focus import(
    ResourceLink, WorkspacePreferences
)

from research.models import ResearchProject

# Create your views here.
@login_required
def dashboard(request):
    user = request.user
    today = timezone.now().date()
    
    pomodoro_settings, _ = PomodoroSettings.objects.get_or_create(user=user)
    workspace_prefs, _ = WorkspacePreferences.objects.get_or_create(user=user)
    
    today_stats, _ = DailyPomodoroStats.objects.get_or_create(
        user=user,
        date=today
    )
    
    streak_days = calculate_streak(user)
    
    week_stats = get_week_stats(user)
    
    today_tasks = Task.objects.filter(
        user=user,
    ).filter(
        Q(due_date__date=today) | Q(due_date__isnull=True, status='in_progress') |
        Q(priority__lte=2, status='todo')
    ).exclude(
        status__in=['done','cancelled']
    ).order_by('priority', 'position')[:10]
    
    
    active_projects = ResearchProject.objects.filter(
        user=user,
        status='active'
    ).order_by('-updated_at')[:5]
    
    recent_notes = Note.objects.filter(
        user=user,
        is_archived=False
    ).select_related('notebook').order_by('-updated_at')[:5]
    
    open_tasks = Task.objects.filter(
        user=user
    ).exclude(
        status__in=['done', 'cancelled']
    ).order_by('priority', '-created_at')[:20]
    
    
    active_session = PomodoroSession.objects.filter(
        user=user,
        status__in=['running', 'paused']
    ).first()
    
    
    context = {
        'today':today,
        'pomodoro_settings':pomodoro_settings,
        'workspace_prefs': workspace_prefs,
        'today_stats':today_stats,
        'streak_days':streak_days,
        'week_stats': week_stats,
        'week_stats_json': json.dumps(week_stats, default=str),
        'todays_tasks':today_tasks,
        'active_projects':active_projects,
        'recent_notes': recent_notes,
        'open_tasks':open_tasks,
        'active_session': active_session
        
    }
    
    return render(request, 'workspace/dashboard_pomodoro.html', context)
    

# POMODORO

@login_required
def pomodoro(request):
    """Dedicated pomodoro timer page"""
    
    user = request.user
    settings, _ = PomodoroSettings.objects.get_or_create(user=user)
    today_stats, _ = DailyPomodoroStats.objects.get_or_create(
        user=user,
        date=timezone.now().date()
    )
    
    #Get active session
    active_session = PomodoroSession.objects.filter(
        user=user,
        status__in=['running', 'paused']
    ).first()
    
    #open task for dropdown
    open_tasks = Task.objects.filter(
        user=user
    ).exclude(
        status__in=['done', 'cancelled']
    ).order_by('priority', '-created_at')[:20]
    
    #Recent Sessions
    recent_sessions = PomodoroSession.objects.filter(
        user=user
    ).order_by('-started_at')[:10]
    
    context = {
        'settings': settings,
        'today_stats': today_stats,
        'active_session': active_session,
        'open_tasks': open_tasks,
        'recent_sessions': recent_sessions,
        'streak_days': calculate_streak(user)
    }
    
    return render(request, 'workspace/pomodoro.html', context)


@login_required
def task_list(request):
    user = request.user
    
    status_filter = request.GET.get('status', 'active')
    list_filter = request.GET.get('list')
    priority_filter = request.GET.get('priority')
    
    # base queryset
    tasks = Task.objects.filter(user=user)
    
    if status_filter == 'active':
        tasks = tasks.exclude(status__in=['done', 'cancelled'])
    elif status_filter == 'done':
        tasks = tasks.filter(status='done')
    elif status_filter != 'all':
        tasks = tasks.filter(status=status_filter)
    
    if list_filter:
        tasks = tasks.filter(task_list__id=list_filter)
        
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    
    tasks = tasks.order_by('priority', 'position', 'created_at')
    
    # Get task list
    task_lists = TaskList.objects.filter(user=user).order_by('position')
    
    context = {
        'tasks': tasks,
        'task_lists': task_lists,
        'status_filter': status_filter,
        'list_filter': list_filter,
        'priority_filter': priority_filter,
    }
    
    return render(request, 'workspace/task.html', context)



@login_required
def note_list(request):
    user = request.user
    
    notebook_filter = request.GET.get('notebook')
    search = request.GET.get('q', '')
    
    notes = Note.objects.filter(user=user, is_archived=False)
    
    if notebook_filter:
        notes = notes.filter(notebook__id=notebook_filter)
        
    if search:
        notes = notes.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search) 
        )
    
    notes = notes.select_related('notebook').order_by('-updated_at')
    
    #Pagination
    paginator = Paginator(notes, 20)
    page = request.GET.get('page',1)
    notes = paginator.get_page(page)
    
    notebooks = Notebook.objects.filter(user=user).order_by('name')
    
    context = {
        'notes': notes,
        'notebooks': notebooks,
        'notebook_filter': notebook_filter,
        'search': search
    }
    
    return render(request, 'workspace/notes.html', context)

@login_required
def note_detail(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    
    versions = NoteVersion.objects.filter(note=note).order_by('-created_at')[:10]
    
    context = {
        'note': note,
        'versions': versions
    }
    return render(request, 'workspace/note_detail.html', context)

    
    
@login_required
def note_create(request):
    if request.method == 'POST':
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        
        notebook = None
        if data.get('notebook_id'):
            notebook = get_object_or_404(Notebook, id=data.get('notebook_id'), user=request.user)
        else:
            notebook,_=Notebook.objects.get_or_create(
                user=request.user,
                is_default=True,
                defaults={'name': 'Quick Notes', 'icon': '📓'}
            )
            
        note = Note.objects.create(
            user=request.user,
            notebook=notebook,
            title=data.get('title', 'Untitled Note'),
            content=data.get('content', ''),
            tags = data.get('tags', [])


        )
        
        if request.content_type == 'application/json':
            return JsonResponse({
                'status': 'success',
                'id': note.id
                
            })
    
        return render(request, 'workspace/note_detail.html')
        
    notebooks = Notebook.objects.filter(user=request.user)
    
    return  render(request, 'workspace/note_create.html', {'notebooks': notebooks})

@login_required
@require_POST
def note_restore(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.is_archived = False
    note.save()
    
    return JsonResponse({
        'status': 'success'
    })


@login_required
@require_POST
def note_delete(request,note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.is_archived = True
    note.save()
    
    return JsonResponse({
        'status': 'success'
    })

@login_required
@require_POST
def note_update(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    data = json.loads(request.body)
    
    if note.content != data.get('content', note.content):
        NoteVersion.objects.create(
            note=note,
            title=note.title,
            content=note.content
        )
    
    if 'title' in data:
        note.title = data['title']
    
    if 'content' in data:
        note.content = data['content']
    
    if 'tags' in data:
        note.tags = data['tags']
    
    if 'notebook_id' in data:
        note.notebook_id = data['notebook_id']
    
    if 'is_pinned' in data:
        note.is_pinned = data['is_pinned']
    
    note.save()
    
    
    return JsonResponse({
        'status': 'success'
    })

@login_required
def settings_page(request):
    pomodoro_settings, _ =PomodoroSettings.objects.get_or_create(user=request.user)
    workspace_prefs, _ = WorkspacePreferences.objects.get_or_create(user=request.user)
    
    context = {
        'pomodoro_settings':pomodoro_settings,
        'workspace_prefs': workspace_prefs,
    }
    
    return render(request, 'workspace/settings.html', context)

@login_required
@require_POST
def preference_update(request):
    
    data = json.loads(request.body)
    prefs, _ = WorkspacePreferences.objects.get_or_create(user=request.user)
    
    if 'theme' in data:
        prefs.theme = data['theme']
    
    if 'sidebar_collapse' in data:
        prefs.sidebar_collapsed = bool(data['sidebar_collapse'])
    
    if 'default_view' in data:
        prefs.default_view = data['default_view']
    
    if 'show_pomodoro_widget' in data:
        prefs.show_pomodoro_widget = bool(data['show_pomodoro_widget'])
    
    if 'show_tasks_widget' in data:
        prefs.show_tasks_widget = bool(data['show_tasks_widget'])
    
    if 'show_calendar_widget' in data:
        prefs.show_calendar_widget = bool(data['show_calendar_widget'])
    
    if 'show_stats_widget' in data:
        prefs.show_stats_widget = bool(data['show_stats_widget'])
    
    if 'show_recent_notes_widget' in data :
        prefs.show_recent_notes_widget =  bool(data['show_recent_notes_widget'])
    
    if 'hide_complete_tasks' in data:
        prefs.hide_completed_tasks = bool(data['hide_complete_tasks'])
    
    prefs.save()
    
    return JsonResponse({'status':'success'})

