from django.urls import include, path, re_path
from .views_api import TelescopeStatusAPI

app_name = 'astronomyapi'

urlpatterns = [
    path('telescope/status/', TelescopeStatusAPI.as_view(), name='telescope_status'),
]