"""services/api_views.py"""
from rest_framework import generics, permissions
from .models import ServiceRequest
from .serializers import ServiceRequestSerializer, ServiceRequestCreateSerializer


class ServiceRequestListCreateAPIView(generics.ListCreateAPIView):
    """GET /api/services/ — list; POST — create a new request."""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ServiceRequestCreateSerializer
        return ServiceRequestSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_customer():
            return ServiceRequest.objects.filter(customer=user).order_by('-created_at')
        elif user.is_provider() and hasattr(user, 'provider_profile'):
            return ServiceRequest.objects.filter(
                provider=user.provider_profile
            ).order_by('-created_at')
        return ServiceRequest.objects.none()


class ServiceRequestDetailAPIView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/services/<id>/"""
    serializer_class = ServiceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_customer():
            return ServiceRequest.objects.filter(customer=user)
        elif user.is_provider() and hasattr(user, 'provider_profile'):
            return ServiceRequest.objects.filter(provider=user.provider_profile)
        return ServiceRequest.objects.none()
