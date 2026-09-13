"""providers/api_views.py — DRF API views for providers."""
from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from .models import ProviderProfile, ServiceCategory
from .serializers import (
    ProviderProfileSerializer,
    ProviderProfileUpdateSerializer,
    ServiceCategorySerializer,
)


class ServiceCategoryListAPIView(generics.ListAPIView):
    """GET /api/providers/categories/ — list all service categories."""
    queryset = ServiceCategory.objects.filter(is_active=True)
    serializer_class = ServiceCategorySerializer
    permission_classes = [permissions.AllowAny]


class ProviderListAPIView(generics.ListAPIView):
    """GET /api/providers/ — list verified providers with filtering."""
    serializer_class = ProviderProfileSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['business_name', 'bio', 'skills__name', 'base_location']
    ordering_fields = ['average_rating', 'experience_years', 'min_charge']
    ordering = ['-average_rating']

    def get_queryset(self):
        qs = ProviderProfile.objects.filter(is_verified=True).select_related(
            'user', 'category'
        ).prefetch_related('skills', 'service_areas', 'availability')

        category = self.request.query_params.get('category')
        location = self.request.query_params.get('location')

        if category:
            qs = qs.filter(category__slug=category)
        if location:
            from django.db.models import Q
            qs = qs.filter(
                Q(base_location__icontains=location) |
                Q(service_areas__area_name__icontains=location)
            ).distinct()
        return qs


class ProviderDetailAPIView(generics.RetrieveAPIView):
    """GET /api/providers/<id>/ — single provider detail."""
    queryset = ProviderProfile.objects.filter(is_verified=True)
    serializer_class = ProviderProfileSerializer
    permission_classes = [permissions.AllowAny]


class MyProviderProfileAPIView(generics.RetrieveUpdateAPIView):
    """GET/PUT /api/providers/me/ — provider updates their own profile."""
    serializer_class = ProviderProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.provider_profile
