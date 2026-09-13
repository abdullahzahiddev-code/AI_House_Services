"""ai_assistant REST API URLs."""
from django.urls import path
from . import api_views

urlpatterns = [
    path('recommend/', api_views.RecommendAPIView.as_view(), name='api_recommend'),
    path('chat/', api_views.ChatAPIView.as_view(), name='api_chat'),
]
