#astronomy/urls.py
from django.urls import path
from .views import (
    gallery,
    observation_detail,
    observation_list
)

app_name = 'astronomy'

urlpatterns = [
    path('', gallery, name='gallery'),
    path('observations/', observation_list, name='observations'),
    path('observations/<slug:slug>/', observation_detail, name='observation_detail'),
]
