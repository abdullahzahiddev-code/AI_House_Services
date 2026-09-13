"""recommendations/api_views.py"""
from rest_framework import generics, permissions
from .models import Recommendation


class RecommendationHistoryAPIView(generics.ListAPIView):
    """GET /api/recommendations/ — User's recommendation history."""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Recommendation.objects.filter(
            conversation__user=self.request.user
        ).select_related('provider', 'conversation').order_by('-created_at')

    def list(self, request, *args, **kwargs):
        from rest_framework.response import Response
        qs = self.get_queryset()
        data = []
        for rec in qs[:20]:
            data.append({
                'id': rec.id,
                'rank': rec.rank,
                'score': rec.score,
                'provider': rec.provider.business_name,
                'provider_id': rec.provider.id,
                'reason': rec.reason,
                'created_at': rec.created_at,
            })
        return Response(data)
