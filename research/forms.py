# research/forms.py
from django import forms
from .models import ResearchProject
import json

class ResearchProjectForm(forms.ModelForm):
    """Form untuk create/edit research project"""
    
    # Custom widget attributes untuk styling
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add CSS classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'
            
            # Add placeholder
            if field_name == 'title':
                field.widget.attrs['placeholder'] = 'e.g., Neural Network for Image Classification'
            elif field_name == 'description':
                field.widget.attrs['placeholder'] = 'Brief description of your research...'
            elif field_name == 'objectives':
                field.widget.attrs['placeholder'] = 'What are the main goals of this research?'
            elif field_name == 'methodology':
                field.widget.attrs['placeholder'] = 'Describe your research methods and approach...'
            elif field_name == 'hypothesis':
                field.widget.attrs['placeholder'] = 'Your hypothesis (if applicable)...'
            elif field_name == 'findings':
                field.widget.attrs['placeholder'] = 'Research findings and results...'
            elif field_name == 'conclusions':
                field.widget.attrs['placeholder'] = 'Your conclusions based on the findings...'
            elif field_name == 'future_work':
                field.widget.attrs['placeholder'] = 'Plans for future research and improvements...'
            elif field_name == 'institution':
                field.widget.attrs['placeholder'] = 'e.g., University of Indonesia'
            elif field_name == 'supervisor':
                field.widget.attrs['placeholder'] = 'e.g., Dr. John Doe'
            elif field_name == 'collaborators':
                field.widget.attrs['placeholder'] = 'List collaborators, one per line'
            elif field_name == 'data_schema':
                field.widget.attrs['placeholder'] = '{"key": "value"}'
                field.widget.attrs['rows'] = 6
    
    class Meta:
        model = ResearchProject
        fields = [
            'title',
            'field',
            'description',
            'objectives',
            'methodology',
            'hypothesis',
            'start_date',
            'end_date',
            'status',
            'priority',
            'progress_percentage',
            'findings',
            'conclusions',
            'future_work',
            'institution',
            'supervisor',
            'collaborators',
            'data_schema',
            'is_public',
            'is_published',
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
            }),
            'field': forms.Select(attrs={
                'class': 'form-select',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
            }),
            'objectives': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
            }),
            'methodology': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
            }),
            'hypothesis': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select',
            }),
            'progress_percentage': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 0,
                'max': 100,
            }),
            'findings': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
            }),
            'conclusions': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
            }),
            'future_work': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
            }),
            'institution': forms.TextInput(attrs={
                'class': 'form-input',
            }),
            'supervisor': forms.TextInput(attrs={
                'class': 'form-input',
            }),
            'collaborators': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
            }),
            'data_schema': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 6,
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
        }
    
    def clean_data_schema(self):
        """Validate JSON data"""
        data_schema = self.cleaned_data.get('data_schema')
        
        if data_schema:
            # If it's already a dict, return it
            if isinstance(data_schema, dict):
                return data_schema
            
            # If it's a string, try to parse it
            if isinstance(data_schema, str):
                data_schema = data_schema.strip()
                if data_schema:
                    try:
                        json.loads(data_schema)
                    except json.JSONDecodeError:
                        raise forms.ValidationError(
                            'Invalid JSON format. Please use valid JSON syntax like {"key": "value"}'
                        )
        
        return data_schema