from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email','website','content')
        widgets = {
            'name': forms.TextInput(attrs={
                'class':'form-input',
                'placeholder': 'Your Name *',
                'required': True
            }),
            'email':forms.EmailInput(attrs={
                'class':'form-input',
                'placeholder': 'Your Email *',
                'required': True
            }),
            'website':forms.URLInput(attrs={
                'class':'form-input',
                'placeholder': 'Your Website (Optional)'
            }),
            'content':forms.Textarea(attrs={
                'class':'form-textarea',
                'placeholder': 'Your Comment *',
                'rows': 5,
                'required': True
            })
        }
        labels = {
            'name': 'Name',
            'email': 'Email',
            'website': 'Website',
            'content': 'Comment'
        }