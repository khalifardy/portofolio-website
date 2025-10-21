# astronomy/forms.py
# Forms untuk data entry penelitian

from django import forms
from django.core.exceptions import ValidationError
from .models import (
    ObservationLog, ResearchProject, ResearchDataEntry, AstroPhoto
)
import json

class ResearchProjectForm(forms.ModelForm):
    """Form untuk membuat research project baru"""
    
    class Meta:
        model = ResearchProject
        fields = ['title', 'research_type', 'description', 'start_date', 
                 'target_duration_days', 'hypothesis', 'expected_results']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Jupiter Moons Orbital Study 2025'}),
            'research_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'target_duration_days': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '30'}),
            'hypothesis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'expected_results': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ObservationLogForm(forms.ModelForm):
    """Form untuk log observasi harian"""
    
    class Meta:
        model = ObservationLog
        fields = ['title', 'observation_date', 'object_name', 'location',
                 'seeing', 'transparency', 'cloud_cover', 'temperature',
                 'telescope', 'eyepiece', 'magnification', 'notes', 'research_project']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'observation_date': forms.DateTimeInput(attrs={
                'class': 'form-control', 
                'type': 'datetime-local'
            }),
            'object_name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'value': 'Bekasi, Indonesia'}),
            'seeing': forms.Select(attrs={'class': 'form-control'}),
            'transparency': forms.Select(attrs={'class': 'form-control'}),
            'cloud_cover': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'temperature': forms.NumberInput(attrs={'class': 'form-control'}),
            'telescope': forms.TextInput(attrs={'class': 'form-control', 'value': 'Celestron 114EQ'}),
            'eyepiece': forms.TextInput(attrs={'class': 'form-control'}),
            'magnification': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'research_project': forms.Select(attrs={'class': 'form-control'}),
        }


class JupiterMoonsDataForm(forms.ModelForm):
    """Specialized form untuk Jupiter Moons data entry"""
    
    # Custom fields untuk Jupiter moons positions
    io_position = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'placeholder': 'e.g., +2.3 (East) or -1.5 (West)'
        }),
        help_text='Position in Jupiter Diameters (DJ). Positive=East, Negative=West'
    )
    
    europa_position = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'placeholder': 'e.g., +3.5'
        }),
        help_text='Position in Jupiter Diameters (DJ)'
    )
    
    ganymede_position = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'placeholder': 'e.g., +4.2'
        }),
        help_text='Position in Jupiter Diameters (DJ)'
    )
    
    callisto_position = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'placeholder': 'e.g., +8.1'
        }),
        help_text='Position in Jupiter Diameters (DJ)'
    )
    
    class Meta:
        model = ResearchDataEntry
        fields = ['observation_datetime', 'data_quality', 'notes']
        widgets = {
            'observation_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'data_quality': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        
        # If editing existing entry, populate custom fields
        if self.instance.pk and self.instance.data:
            self.fields['io_position'].initial = self.instance.data.get('io')
            self.fields['europa_position'].initial = self.instance.data.get('europa')
            self.fields['ganymede_position'].initial = self.instance.data.get('ganymede')
            self.fields['callisto_position'].initial = self.instance.data.get('callisto')
    
    def clean(self):
        cleaned_data = super().clean()
        
        # At least one moon position must be provided
        positions = [
            cleaned_data.get('io_position'),
            cleaned_data.get('europa_position'),
            cleaned_data.get('ganymede_position'),
            cleaned_data.get('callisto_position'),
        ]
        
        if not any(positions):
            raise ValidationError("At least one moon position must be provided")
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Build data JSON from custom fields
        instance.data = {}
        if self.cleaned_data.get('io_position') is not None:
            instance.data['io'] = self.cleaned_data['io_position']
        if self.cleaned_data.get('europa_position') is not None:
            instance.data['europa'] = self.cleaned_data['europa_position']
        if self.cleaned_data.get('ganymede_position') is not None:
            instance.data['ganymede'] = self.cleaned_data['ganymede_position']
        if self.cleaned_data.get('callisto_position') is not None:
            instance.data['callisto'] = self.cleaned_data['callisto_position']
        
        if self.project:
            instance.project = self.project
        
        if commit:
            instance.save()
        return instance


class VariableStarDataForm(forms.ModelForm):
    """Form untuk variable star magnitude estimates"""
    
    magnitude = forms.FloatField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'placeholder': 'e.g., 3.2'
        }),
        help_text='Estimated magnitude'
    )
    
    comparison_star = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., SAO 12345'
        }),
        help_text='Comparison star used'
    )
    
    class Meta:
        model = ResearchDataEntry
        fields = ['observation_datetime', 'data_quality', 'notes']
        widgets = {
            'observation_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'data_quality': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        instance.data = {
            'magnitude': self.cleaned_data['magnitude'],
        }
        if self.cleaned_data.get('comparison_star'):
            instance.data['comparison_star'] = self.cleaned_data['comparison_star']
        
        if commit:
            instance.save()
        return instance


class MeteorCountDataForm(forms.ModelForm):
    """Form untuk meteor shower observations"""
    
    meteor_count = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Total meteors observed'
        }),
        help_text='Total number of meteors'
    )
    
    sporadic_count = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='Number of sporadic meteors (not from radiant)'
    )
    
    fireball_count = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='Number of fireballs (mag < -3)'
    )
    
    limiting_magnitude = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1'
        }),
        help_text='Faintest visible star magnitude'
    )
    
    observation_duration_minutes = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='Duration of observation in minutes'
    )
    
    class Meta:
        model = ResearchDataEntry
        fields = ['observation_datetime', 'data_quality', 'notes']
        widgets = {
            'observation_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'data_quality': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        instance.data = {
            'meteor_count': self.cleaned_data['meteor_count'],
            'observation_duration': self.cleaned_data['observation_duration_minutes'],
        }
        
        if self.cleaned_data.get('sporadic_count') is not None:
            instance.data['sporadic_count'] = self.cleaned_data['sporadic_count']
        if self.cleaned_data.get('fireball_count') is not None:
            instance.data['fireball_count'] = self.cleaned_data['fireball_count']
        if self.cleaned_data.get('limiting_magnitude') is not None:
            instance.data['limiting_magnitude'] = self.cleaned_data['limiting_magnitude']
        
        # Calculate ZHR estimate
        shower_count = instance.data['meteor_count'] - instance.data.get('sporadic_count', 0)
        duration_hours = instance.data['observation_duration'] / 60.0
        if duration_hours > 0:
            instance.data['zhr_estimate'] = round(shower_count / duration_hours, 1)
        
        if commit:
            instance.save()
        return instance


class AstroPhotoUploadForm(forms.ModelForm):
    """Form untuk upload astrofotografi"""
    
    class Meta:
        model = AstroPhoto
        fields = ['title', 'image', 'capture_date', 'description',
                 'exposure_time', 'iso', 'aperture', 'focal_length',
                 'processing_notes', 'sequence_number']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'capture_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'exposure_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1/125s or 30s'}),
            'iso': forms.NumberInput(attrs={'class': 'form-control'}),
            'aperture': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'f/8'}),
            'focal_length': forms.NumberInput(attrs={'class': 'form-control'}),
            'processing_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'sequence_number': forms.NumberInput(attrs={'class': 'form-control'}),
        }


# ==================== HELPER FUNCTIONS ====================

def get_form_for_research_type(research_type):
    """Return appropriate data entry form based on research type"""
    form_mapping = {
        'orbital': JupiterMoonsDataForm,
        'variable_star': VariableStarDataForm,
        'meteor': MeteorCountDataForm,
    }
    return form_mapping.get(research_type, forms.ModelForm)


# ==================== MULTI-ENTRY FORMSET ====================

from django.forms import formset_factory

# Create formset for bulk data entry
JupiterMoonsDataFormSet = formset_factory(
    JupiterMoonsDataForm,
    extra=5,  # Show 5 empty forms by default
    can_delete=True
)