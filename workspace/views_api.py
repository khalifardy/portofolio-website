from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import PomodoroSettings, PomodoroSession, Task, DailyPomodoroStats, TaskList, Note, NoteVersion, Notebook
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime

from library_helper.workspace import calculate_streak, get_week_stats
class PomodoroView(APIView):
    permission_classes = [IsAuthenticated]
    
    def start(self,request):
        user = request.user
        session_type = request.data.get('session_type','work')
        task_id = request.data.get('task_id',None)
        
        PomodoroSession.objects.filter(
            user=user,
            status__in=['running', 'paused']
        ).update(status='cancelled',ended_at=timezone.now())
        
        settings, _ = PomodoroSettings.objects.get_or_create(user=user)
        
        
        if session_type =='work':
            duration = settings.work_duration * 60
        elif session_type =='short_break':
            duration = settings.short_break_duration * 60
        else:
            duration = settings.long_break_duration * 60
        
        
        #create session
        session = PomodoroSession.objects.create(
            user=user,
            session_type=session_type,
            planned_duration=duration,
            status='running',
            started_at=timezone.now(),
        )
        
        if task_id:
            try:
                task = Task.objects.get(id=task_id,user=user)
                session.task = task
                session.save()
            except Task.DoesNotExist:
                pass
        
        return Response({
            'status':'success',
            'session_id':session.id,
            'session_type':session.session_type,
            'duration':duration,
            'started_at':session.started_at.isoformat()
        }, status=status.HTTP_200_OK)
    
    def pause(self,request):
        session_id = request.data.get('session_id')
        session = get_object_or_404(PomodoroSession, id=session_id, user=request.user)
        
        if session.status != 'running':
            session.pause()
            return Response({
                'status':'success',
                'time_remaining':session.time_remaining
            }, status=status.HTTP_200_OK)
            
        return Response({
            'status':'error',
            'message':'Session is not running'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def resume(self, request):
        session_id = request.data.get('session_id')
        session = get_object_or_404(PomodoroSession, id=session_id, user=request.user)
        
        if session.status == 'paused':
            session.resume()
            return Response({
                'status':'success',
                'time_remaining':session.started_at.isoformat()
            }, status=status.HTTP_200_OK)
        
        return Response({
            'status':'error',
            'message':'Session is not running'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    
    def complete(self,request):
        session_id = request.data.get('session_id')
        session = get_object_or_404(PomodoroSession, id=session_id, user=request.user)
        
        if session.status == 'running':
            session.complete()
            return Response({
                'status':'success',
                'time_remaining':session.started_at.isoformat()
            }, status=status.HTTP_200_OK)
        
        return Response({
            'status':'error',
            'message':'Session is not running'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def cancel(self,request):
        session_id = request.data.get('session_id')
        session = get_object_or_404(PomodoroSession, id=session_id, user=request.user)
        session.cancel()
        
        DailyPomodoroStats.update_for_session(session)
        return Response({
            'status':'success'
        })
    
    def settings_update(self, request):
        user = request.user
        data = request.data
        
        settings, _ = PomodoroSettings.objects.get_or_create(user=user)
        
        if 'work_duration' in data:
            settings.work_duration = int(data['work_duration'])
        if 'short_break_duration' in data:
            settings.short_break_duration = int(data['short_break_duration'])
        if 'long_break_duration' in data:
            settings.long_break_duration = int(data['long_break_duration'])
        if 'pomodoro_before_long_break' in data:
            settings.pomodoro_before_long_break = int(data['pomodoro_before_long_break'])
        if 'daily_pomodoro_goal' in data:
            settings.daily_pomodoro_goal = int(data['daily_pomodoro_goal'])
        if 'auto_start_breaks' in data:
            settings.auto_start_breaks = bool(data['auto_start_breaks'])
        if 'auto_start_pomodoro' in data:
            settings.auto_start_pomodoro = bool(data['auto_start_pomodoro'])
        if 'sound_enabled' in data:
            settings.sound_enabled = bool(data['sound_enabled'])
        
        settings.save()
        
        return Response({
            'status':'success'
        })
    
    def post(self,request):
        action = request.data.get('action')
        if action == 'start':
            return self.start(request)
        elif action == 'pause':
            return self.pause(request)
        elif action == 'resume':
            return self.resume(request)
        elif action == 'complete':
            return self.complete(request)
        elif action == 'cancel':
            return self.cancel(request)
        elif action == 'settings_update':
            return self.settings_update(request)
        else:
            return Response({
                'status':'error',
                'message':'Invalid action'
            }, status=status.HTTP_400_BAD_REQUEST)


class TaskView(APIView):
    permission_classes = [IsAuthenticated]
    
    
    def task_create(self, request):
        data_ = request.data
        user = request.user
        
        task_list = None
        if data_.get('task_list_id'):
            task_list = get_object_or_404(TaskList, id=data_['task_list_id'], user=user)
        else:
            task_list, _ = TaskList.objects.get_or_create(
                user=user,
                is_default=True,
                defaults={'name':'Inbox', 'icon':'📥'}
            )
        
        due_date = None
        if data_.get('due_date'):
            try:
                due_date = datetime.fromisoformat(data_['due_date'].replace('Z','+00:00'))
            except:
                pass
        
        task = Task.objects.create(
            user=user,
            title=data_.get('title', 'Untitled Task'),
            description=data_.get('description'),
            priority=data_.get('priority', 3),
            status='todo',
            due_date=due_date,
            estimated_pomodoros=data_.get('estimated_pomodoros', 1),
            tags=data_.get('tags', []),
            task_list=task_list
        )    
        
        return Response({
            'status':'success',
            'task_id':task.id,
            'task':{
                'id':task.id,
                'title':task.title,
                'priority':task.priority,
                'status':task.status,
            }
        })
    
    
    def task_complete(self, request, task_id):
        task = get_object_or_404(Task, id=task_id, user=request.user)
        task.status = 'done'
        task.completed_at = timezone.now()
        task.save()
        
        return Response({
            'status':'success'
        })
    
    def task_reorder(self,request):
        data_ = request.data
        tasks_ids = data_.get('tasks_ids', [])
        
        for position, task_id  in enumerate(tasks_ids):
            Task.objects.filter(
                id=task_id,
                user=request.user
            ).update(position=position)
        
        return Response({
            'status':'success'
        })
    
    def post(self, request, format=None):
        action = request.data.get('action')
        if action == 'create':
            return self.task_create(request)
        elif action == 'complete':
            return self.task_complete(request, request.data.get('task_id'))
        elif action == 'reorder':
            return self.task_reorder(request)
        else:
            return Response({
                'status':'error',
                'message':'Invalid action'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self,request, task_id):
        data_ = request.data
        task = get_object_or_404(Task, id=task_id, user=self.request.user)
        
        if 'title' in data_:
            task.title = data_['title']
        
        if 'description' in data_:
            task.description = data_['description']
        
        if 'priority' in data_:
            task.priority = data_['priority']
        
        if 'status' in data_:
            task.status = data_['status']
            if data_['status'] == 'done':
                task.completed_at = timezone.now()
        
        if 'due_date' in data_:
            if data_['due_date']:
                try:
                    task.due_date = datetime.fromisoformat(data_['due_date'].replace('Z','+00:00'))
                except:
                    pass
            else:
                task.due_date = None
        
        if 'estimated_pomodoros' in data_ :
            task.estimated_pomodoros = int(data_['estimated_pomodoros'])
        
        if 'tags' in data_:
            task.tags = data_['tags']
        
        if 'task_list_id' in data_:
            task.task_list_id = data_['task_list_id']
            
        task.save()
        
        return Response({
            'status':'success'
        })
    
    def delete(self, request, task_id):
        task = get_object_or_404(Task, id=task_id, user=self.request.user)
        task.delete()
        
        return Response({
            'status':'success'
        })

class NotesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def restore(self, request, note_id):
        note = get_object_or_404(Note, id=note_id, user=request.user)
        note.is_archived = False
        note.save()
        
        return Response({
            'status':'success'
        })
    
    def post(self, request, note_id):
        return self.restore(request, note_id)
    
    def update(self, request, note_id):
        data = request.data
        note = get_object_or_404(Note, id=note_id, user=request.user)
        
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
        
        if 'is_pinned' in data :
            note.is_pinned = data['is_pinned']
        
        note.save()
        
        return Response({
            'status':'success'
        })
        
        
    def delete(self, request, note_id):
        note = get_object_or_404(Note, id=note_id, user=request.user)
        note.is_archived = True
        note.save()
        
        return Response({
            'status':'success'
        })
    


class NotebooksView(APIView):
    permission_classes = [IsAuthenticated]
    
    
    def post(self, request, notebook_id):
        
        data = request.data.get('name', 'New Notebook')
        icon = request.data.get('icon', '📓')
        color = request.data.get('color', '#37a749')
        
        
        notebook = Notebook.objects.create(
            user=request.user,
            name=data,
            icon=icon,
            color=color
        )
        
        return Response({
            'status':'success',
            'notebook_id':notebook.id
        })
    
    def update(self,request,notebppk_id):
        
        notebook = get_object_or_404(Notebook, id=notebppk_id, user=request.user)
        name = request.data.get('name', notebook.name)
        icon = request.data.get('icon', notebook.icon)
        color = request.data.get('color', notebook.color)
        
        notebook.name = name
        notebook.icon = icon
        notebook.color = color
        notebook.save()
        
        return Response({
            'status':'success'
        })
    
    def delete(self, request, notebook_id):
        notebook = get_object_or_404(Notebook, id=notebook_id, user=request.user)
        
        if notebook.is_default:
            return Response({
                'status':'error',
                'message':'Cannot delete default notebook'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        default_notebook, _ = Notebook.objects.get_or_create(
            user=request.user,
            is_default=True,
            defaults={'name': 'Quick Notes', 'icon': '📓'}
        )
        
        Note.objects.filter(notebook=notebook).update(notebook=default_notebook)
        notebook.delete()
        
        return Response({
            'status':'success'
        })

class StatsView(APIView):
    
    permission_classes = [IsAuthenticated,]
    
    def api_stats(self,request):
        user = request.user
        today = timezone.now().date()
        
        today_stats, _ = DailyPomodoroStats.objects.get_or_create(
            user=user,
            date=today
        )
        
        respon = {
            'streak_days': calculate_streak(user),
            'today':{
                'complete_pomodoro': today_stats.completed_pomodoros,
                'total_focus_minutes': today_stats.total_focus_minutes,
                'goal_met': today_stats.goal_met
            },
            'week_stats': get_week_stats(user),
            'open_tasks': Task.objects.filter(
                user=user
            ).exclude(
                status_in=['done','cancelled']
            ).count(),
        }
        
        return Response(respon)
    
    def api_active_session(self,request):
        session = PomodoroSession.objects.filter(
            user=request.user,
            status__in = ['running', 'paused']
        ).first()
        
        if session:
            respon = {
                'active':True,
                'session': {
                    'id':session.id,
                    'session_type': session.session_type,
                    'status':session.status,
                    'planned_duration': session.planned_duration,
                    'time_remaining':session.time_remaining,
                    'started_at': session.started_at.isoformat() if session.started_at else None,
                    'task_id': session.task_id,
                    'task_title': session.task.title if session.task else None
                }
            }
            
            return Response(respon)
    
    def get(self, request):
        tipe_stat = request.data.get('tipe_stat')
        
        if tipe_stat == 'stats':
            return self.api_stats(request)
        elif tipe_stat == 'active_session':
            return self.api_active_session(request)
    
    