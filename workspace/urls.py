from django.urls import path
from .views import(dashboard, pomodoro, task_list, note_list, settings_page, preference_update, note_create)

app_name = 'workspace'

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('pomodoro/', pomodoro, name='pomodoro'),
    path('tasks/', task_list, name='task_list'),
    path('notes/', note_list, name='note_list'),
    path('notes/create/', note_create, name='note_create'),
    path('settings/', settings_page, name='settings'),
    path('preference/update/', preference_update, name='preference_update'),
]
