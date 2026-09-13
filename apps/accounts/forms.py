"""
accounts/forms.py — Registration and login forms.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, CustomerProfile


class CustomerRegistrationForm(UserCreationForm):
    """Form for customer registration."""
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=20, required=False)
    location = forms.CharField(max_length=200, required=False, help_text="Your city or area")

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',
                  'phone_number', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.CUSTOMER
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data.get('phone_number', '')
        if commit:
            user.save()
            CustomerProfile.objects.create(
                user=user,
                location=self.cleaned_data.get('location', ''),
            )
        return user


class ProviderRegistrationForm(UserCreationForm):
    """Form for service provider registration."""
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=20, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',
                  'phone_number', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.PROVIDER
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data.get('phone_number', '')
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    """Form to update basic user info."""
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'profile_picture')


class CustomerProfileForm(forms.ModelForm):
    """Form to update customer profile."""
    class Meta:
        model = CustomerProfile
        fields = ('location', 'full_address', 'preferred_contact')


class LoginForm(AuthenticationForm):
    """Custom login form with Bootstrap styling."""
    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username'}
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}
    ))
