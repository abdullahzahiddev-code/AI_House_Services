"""reviews/api_views.py"""
from rest_framework import generics, permissions
from .models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer


class ReviewListAPIView(generics.ListAPIView):
    """GET /api/reviews/?provider=<id>"""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Review.objects.filter(is_verified=True).select_related('reviewer', 'provider')
        provider_id = self.request.query_params.get('provider')
        if provider_id:
            qs = qs.filter(provider_id=provider_id)
        return qs.order_by('-created_at')


class ReviewCreateAPIView(generics.CreateAPIView):
    """POST /api/reviews/"""
    serializer_class = ReviewCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
