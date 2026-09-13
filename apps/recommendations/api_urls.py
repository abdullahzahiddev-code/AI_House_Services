"""recommendations REST API URLs."""
from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.RecommendationHistoryAPIView.as_view(), name='api_recommendation_history'),
]
