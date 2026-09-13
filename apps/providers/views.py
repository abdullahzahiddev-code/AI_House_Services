"""
providers/views.py — Provider profile views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import ProviderProfile, ServiceCategory, ServiceArea, Availability, Skill
from .forms import (
    ProviderProfileForm,
    ServiceAreaFormSet,
    AvailabilityFormSet,
)


def provider_list(request):
    """Public page listing all verified service providers."""
    category_slug = request.GET.get('category', '')
    location = request.GET.get('location', '')
    search = request.GET.get('q', '')

    providers = ProviderProfile.objects.filter(is_verified=True).select_related(
        'user', 'category'
    ).prefetch_related('skills', 'service_areas')

    if category_slug:
        providers = providers.filter(category__slug=category_slug)
    if location:
        providers = providers.filter(
            Q(base_location__icontains=location) |
            Q(service_areas__area_name__icontains=location)
        ).distinct()
    if search:
        providers = providers.filter(
            Q(business_name__icontains=search) |
            Q(bio__icontains=search) |
            Q(skills__name__icontains=search)
        ).distinct()

    categories = ServiceCategory.objects.filter(is_active=True)

    context = {
        'providers': providers,
        'categories': categories,
        'selected_category': category_slug,
        'location': location,
        'search': search,
    }
    return render(request, 'providers/provider_list.html', context)


def provider_detail(request, pk):
    """Public profile page for a single provider."""
    provider = get_object_or_404(
        ProviderProfile.objects.select_related('user', 'category')
        .prefetch_related('skills', 'service_areas', 'availability'),
        pk=pk,
        is_verified=True,
    )
    reviews = provider.reviews.select_related('reviewer').order_by('-created_at')[:10]
    context = {
        'provider': provider,
        'reviews': reviews,
    }
    return render(request, 'providers/provider_detail.html', context)


@login_required
def setup_profile(request):
    """Provider: create or complete their profile after registration."""
    if not request.user.is_provider():
        messages.error(request, "Only service providers can access this page.")
        return redirect('core:dashboard')

    profile, created = ProviderProfile.objects.get_or_create(
        user=request.user,
        defaults={'business_name': request.user.get_full_name() or request.user.username}
    )

    if request.method == 'POST':
        form = ProviderProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('providers:dashboard')
    else:
        form = ProviderProfileForm(instance=profile)

    return render(request, 'providers/setup_profile.html', {'form': form, 'profile': profile})


@login_required
def provider_dashboard(request):
    """Provider dashboard — overview of their profile and requests."""
    if not request.user.is_provider():
        return redirect('core:dashboard')

    try:
        profile = request.user.provider_profile
    except ProviderProfile.DoesNotExist:
        return redirect('providers:setup_profile')

    pending_requests = profile.service_requests.filter(
        status='PENDING'
    ).select_related('customer', 'category').order_by('-created_at')[:5]

    recent_reviews = profile.reviews.order_by('-created_at')[:5]

    context = {
        'profile': profile,
        'pending_requests': pending_requests,
        'recent_reviews': recent_reviews,
    }
    return render(request, 'providers/dashboard.html', context)


@login_required
def manage_service_areas(request):
    """Provider: manage their service areas."""
    if not request.user.is_provider():
        return redirect('core:dashboard')

    profile = get_object_or_404(ProviderProfile, user=request.user)
    areas = profile.service_areas.all()

    if request.method == 'POST':
        area_name = request.POST.get('area_name', '').strip()
        city = request.POST.get('city', 'Rawalpindi').strip()
        if area_name:
            ServiceArea.objects.get_or_create(
                provider=profile, area_name=area_name,
                defaults={'city': city}
            )
            messages.success(request, f"'{area_name}' added to your service areas.")
        return redirect('providers:manage_service_areas')

    return render(request, 'providers/manage_service_areas.html', {
        'profile': profile, 'areas': areas
    })


@login_required
def delete_service_area(request, pk):
    """Provider: delete a service area."""
    area = get_object_or_404(ServiceArea, pk=pk, provider__user=request.user)
    area.delete()
    messages.success(request, "Service area removed.")
    return redirect('providers:manage_service_areas')
