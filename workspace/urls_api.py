from django.urls import include, path, re_path
from .views_api import PomodoroView, NotesView, TaskView, StatsView, NotebooksView

app_name = 'workspace_api'

urlpatterns = [
    path('pomodoro/', PomodoroView.as_view(), name='pomodoro'),
    path('notes/', NotesView.as_view(), name='notes'),
    path('tasks/', TaskView.as_view(), name='tasks'),
    path('notebooks/', NotebooksView.as_view(), name='notebooks'),
    path('stat/', StatsView.as_view(), name='stats')
]