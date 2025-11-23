#astronomy/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import (
    AstroPhoto,
    ObservationLog,
    CelestialObjects
)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.decorators import login_required

import socket
import subprocess
# Create your views here.

def gallery(request):
    """Astrophotography gallery page"""
    
    photos = AstroPhoto.objects.filter(is_public=True).order_by('-capture_date')
    
    # Filter by object type if provided
    object_type = request.GET.get('type')
    if object_type:
        photos = photos.filter(celestial_objects__object_type=object_type)
    
    # Pagination
    paginator = Paginator(photos, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get object types for filter
    object_types = CelestialObjects.OBJECT_TYPES
    
    context = {
        'page_obj':page_obj,
        'object_types' : object_types,
        'current_type': object_type
    }
    
    return render(request, 'astronomy/gallery.html', context)

def observation_list(request):
    """List of all observation logs"""
    observations = ObservationLog.objects.filter(is_public=True).order_by('-observation_date')
    
    #Pagination
    paginator = Paginator(observations, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    
    context = {
        'page_obj':page_obj
    }
    
    return render(request, 'astronomy/observations.html', context)

def observation_detail(request, slug):
    """Detail view for single observation"""
    
    observation = get_object_or_404(ObservationLog, slug=slug, is_public=True)
    photos = observation.photos.all()
    
    #Get other observations of same object
    related_observations = ObservationLog.objects.filter(
        celestial_object=observation.celestial_object,
        is_public=True
    ).exclude(id=observation.id)[:3]
    
    context = {
        'observation': observation,
        'photos': photos,
        'related_observations': related_observations
    }
    
    return render(request, 'astronomy/observation_detail.html', context)

def check_telescope_status():
    
    status = {
        'tunnel_active': False,
        'vnc_active': False,
        'message': ''
    }
    
    try:
        
        host_to_try = [
            'host.docker.internal',
            '172.17.0.1',
            'localhost'
        ]
        
        for host in host_to_try:
        #cek port 15900 listening 
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex((host, 15900))
                    status['tunnel_active'] = (result==0)
                    if result==0:
                        break
            except:
                continue
            
        for host in host_to_try:
            #cek port 6080 listening
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex((host, 6080))
                    status['vnc_active'] = (result==0)
                    if result==0:
                        break
            except:
                continue
            
            
        if status['tunnel_active'] and status['vnc_active']:
            status['message'] = "Telescope connection active" 
        elif status['vnc_active'] and not status['tunnel_active']:
            status['message'] = "waiting for Astrobery connection" 
        else:
            status['message'] = "SERVICE UNAVAILABLE"
    
    except Exception as e:
        status['message'] = f"errorchecking status: {str}"
    
    return status

@login_required
def telescope_remote_access(request):
    """remote telescope access page with noVNC viewer"""
    
    context = {
        'title': 'Remote Telescope Access',
        'vnc_url':'https://astro/ideasophia.com/vnc.html',
        'status': check_telescope_status()
    }
    
    return render(request, 'astronomy/telescope_remote.html', context)