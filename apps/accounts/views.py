"""
accounts/views.py — Auth views: register, login, logout, profile.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy

from .forms import (
    CustomerRegistrationForm,
    ProviderRegistrationForm,
    UserUpdateForm,
    CustomerProfileForm,
    LoginForm,
)
from .models import User, CustomerProfile


def register_customer(request):
    """Register a new customer account."""
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name}! Your account has been created.")
            return redirect('core:dashboard')
    else:
        form = CustomerRegistrationForm()

    return render(request, 'accounts/register_customer.html', {'form': form})


def register_provider(request):
    """Register a new service provider account."""
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = ProviderRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f"Welcome, {user.first_name}! Please complete your provider profile."
            )
            return redirect('providers:setup_profile')
    else:
        form = ProviderRegistrationForm()

    return render(request, 'accounts/register_provider.html', {'form': form})


def user_login(request):
    """Login view."""
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next', 'core:dashboard')
            return redirect(next_url)
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    """Logout view."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('core:home')


@login_required
def profile(request):
    """View and update user profile."""
    user = request.user

    # Get or create the customer profile if applicable
    customer_profile = None
    if user.is_customer():
        customer_profile, _ = CustomerProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, request.FILES, instance=user)
        profile_form = CustomerProfileForm(
            request.POST, instance=customer_profile
        ) if customer_profile else None

        if user_form.is_valid():
            user_form.save()
            if profile_form and profile_form.is_valid():
                profile_form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = CustomerProfileForm(instance=customer_profile) if customer_profile else None

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'customer_profile': customer_profile,
    }
    return render(request, 'accounts/profile.html', context)
