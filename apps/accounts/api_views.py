"""accounts/api_views.py — DRF API views for auth."""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import (
    CustomerRegisterSerializer,
    ProviderRegisterSerializer,
    UserSerializer,
)


class CustomerRegisterAPIView(generics.CreateAPIView):
    """POST /api/auth/register/customer/ — Register a new customer."""
    serializer_class = CustomerRegisterSerializer
    permission_classes = [permissions.AllowAny]


class ProviderRegisterAPIView(generics.CreateAPIView):
    """POST /api/auth/register/provider/ — Register a new service provider."""
    serializer_class = ProviderRegisterSerializer
    permission_classes = [permissions.AllowAny]


class CurrentUserAPIView(APIView):
    """GET /api/auth/me/ — Return the currently authenticated user."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
