"""services/views.py — Service request views."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ServiceRequest
from .forms import ServiceRequestForm


@login_required
def create_request(request):
    """Customer creates a new service request."""
    if not request.user.is_customer():
        messages.error(request, "Only customers can create service requests.")
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.customer = request.user
            service_request.save()
            messages.success(request, "Service request submitted successfully!")
            return redirect('services:my_requests')
    else:
        # Pre-fill location from customer profile if available
        initial = {}
        try:
            initial['location'] = request.user.customer_profile.location
        except Exception:
            pass
        form = ServiceRequestForm(initial=initial)

    return render(request, 'services/create_request.html', {'form': form})


@login_required
def my_requests(request):
    """Customer views their own service requests."""
    if request.user.is_customer():
        requests_qs = ServiceRequest.objects.filter(
            customer=request.user
        ).select_related('category', 'provider').order_by('-created_at')
    elif request.user.is_provider():
        try:
            provider = request.user.provider_profile
            requests_qs = ServiceRequest.objects.filter(
                provider=provider
            ).select_related('customer', 'category').order_by('-created_at')
        except Exception:
            requests_qs = ServiceRequest.objects.none()
    else:
        requests_qs = ServiceRequest.objects.none()

    return render(request, 'services/my_requests.html', {'requests': requests_qs})


@login_required
def request_detail(request, pk):
    """View details of a single service request."""
    service_request = get_object_or_404(ServiceRequest, pk=pk)

    # Permission check
    is_customer = service_request.customer == request.user
    is_provider = (
        request.user.is_provider() and
        hasattr(request.user, 'provider_profile') and
        service_request.provider == request.user.provider_profile
    )
    if not (is_customer or is_provider or request.user.is_staff):
        messages.error(request, "You don't have permission to view this request.")
        return redirect('services:my_requests')

    return render(request, 'services/request_detail.html', {
        'request_obj': service_request,
        'is_customer': is_customer,
        'is_provider': is_provider,
    })


@login_required
def update_request_status(request, pk):
    """Provider accepts/rejects/completes a service request."""
    service_request = get_object_or_404(ServiceRequest, pk=pk)

    if not request.user.is_provider():
        messages.error(request, "Only providers can update request status.")
        return redirect('services:my_requests')

    new_status = request.POST.get('status')
    notes = request.POST.get('notes', '')
    valid_transitions = {
        'PENDING': ['ACCEPTED', 'REJECTED'],
        'ACCEPTED': ['IN_PROGRESS', 'CANCELLED'],
        'IN_PROGRESS': ['COMPLETED', 'CANCELLED'],
    }

    allowed = valid_transitions.get(service_request.status, [])
    if new_status in allowed:
        service_request.status = new_status
        service_request.provider_notes = notes
        service_request.save()
        messages.success(request, f"Request status updated to {new_status}.")
    else:
        messages.error(request, "Invalid status transition.")

    return redirect('services:request_detail', pk=pk)


@login_required
def cancel_request(request, pk):
    """Customer cancels their request."""
    service_request = get_object_or_404(ServiceRequest, pk=pk, customer=request.user)
    if service_request.status in ('PENDING', 'ACCEPTED'):
        service_request.status = 'CANCELLED'
        service_request.save()
        messages.success(request, "Request cancelled.")
    else:
        messages.error(request, "Cannot cancel a request in its current state.")
    return redirect('services:my_requests')
