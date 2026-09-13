"""core/views.py — Home page and dashboard."""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.providers.models import ServiceCategory, ProviderProfile


def home(request):
    """Public home page."""
    categories = ServiceCategory.objects.filter(is_active=True)[:8]
    top_providers = ProviderProfile.objects.filter(
        is_verified=True
    ).order_by('-average_rating')[:6]
    return render(request, 'core/home.html', {
        'categories': categories,
        'top_providers': top_providers,
    })


@login_required
def dashboard(request):
    """Role-based dashboard redirect."""
    if request.user.is_provider():
        return redirect('providers:dashboard')
    elif request.user.is_customer():
        return render(request, 'core/customer_dashboard.html', {
            'recent_requests': request.user.service_requests.order_by('-created_at')[:5],
            'recent_conversations': request.user.ai_conversations.order_by('-created_at')[:3],
        })
    return redirect('core:home')


def about(request):
    return render(request, 'core/about.html')
