"""services/forms.py"""
from django import forms
from .models import ServiceRequest


class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = (
            'problem_description', 'location', 'category',
            'preferred_date', 'preferred_time',
        )
        widgets = {
            'problem_description': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Describe your home problem in detail...'
            }),
            'location': forms.TextInput(attrs={'placeholder': 'e.g., Bahria Town Phase 4'}),
            'preferred_date': forms.DateInput(attrs={'type': 'date'}),
            'preferred_time': forms.TimeInput(attrs={'type': 'time'}),
        }
