"""reviews/views.py"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.services.models import ServiceRequest
from apps.providers.models import ProviderProfile
from .models import Review
from .forms import ReviewForm


@login_required
def submit_review(request, request_pk):
    """Customer submits a review for a completed service."""
    service_request = get_object_or_404(
        ServiceRequest, pk=request_pk, customer=request.user
    )

    if not service_request.can_review():
        messages.error(request, "You can only review completed services.")
        return redirect('services:request_detail', pk=request_pk)

    # Check if already reviewed
    if hasattr(service_request, 'review'):
        messages.info(request, "You have already submitted a review for this service.")
        return redirect('services:request_detail', pk=request_pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.service_request = service_request
            review.reviewer = request.user
            review.provider = service_request.provider
            review.save()
            messages.success(request, "Thank you for your review!")
            return redirect('services:request_detail', pk=request_pk)
    else:
        form = ReviewForm()

    return render(request, 'reviews/submit_review.html', {
        'form': form,
        'service_request': service_request,
    })


def provider_reviews(request, provider_pk):
    """Public page showing all reviews for a provider."""
    provider = get_object_or_404(ProviderProfile, pk=provider_pk, is_verified=True)
    reviews = provider.reviews.filter(is_verified=True).select_related('reviewer')
    return render(request, 'reviews/provider_reviews.html', {
        'provider': provider,
        'reviews': reviews,
    })
