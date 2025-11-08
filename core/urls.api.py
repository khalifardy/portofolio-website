from django.urls import include, path, re_path
from .views_api import LogoutView

urlpatterns = [
    path('logout/', LogoutView.as_view(), name='logout'),
]