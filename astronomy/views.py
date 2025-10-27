#astronomy/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import (
    AstroPhoto,
    ObservationLog,
    CelestialObjects
)
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

