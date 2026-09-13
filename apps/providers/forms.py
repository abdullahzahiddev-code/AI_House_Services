"""providers/forms.py — Provider profile forms."""
from django import forms
from .models import ProviderProfile, ServiceArea, Availability


class ProviderProfileForm(forms.ModelForm):
    """Main form for provider to fill in their professional details."""

    class Meta:
        model = ProviderProfile
        fields = [
            'business_name', 'category', 'bio',
            'experience_years', 'skills',
            'phone_number', 'whatsapp_number', 'email',
            'base_location', 'min_charge', 'max_charge',
            'is_available', 'profile_picture',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'skills': forms.CheckboxSelectMultiple(),
            'experience_years': forms.NumberInput(attrs={'min': 0, 'max': 50}),
        }
        help_texts = {
            'min_charge': 'Minimum service charge in PKR (e.g., 1500)',
            'max_charge': 'Maximum service charge in PKR (e.g., 5000)',
            'skills': 'Select all skills that apply to your service category',
        }


# Simple inline formsets
ServiceAreaFormSet = forms.inlineformset_factory(
    ProviderProfile,
    ServiceArea,
    fields=('area_name', 'city'),
    extra=2,
    can_delete=True,
)

AvailabilityFormSet = forms.inlineformset_factory(
    ProviderProfile,
    Availability,
    fields=('day', 'start_time', 'end_time', 'is_available'),
    extra=1,
    can_delete=True,
)
