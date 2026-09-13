"""reviews REST API URLs."""
from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.ReviewListAPIView.as_view(), name='api_reviews_list'),
    path('create/', api_views.ReviewCreateAPIView.as_view(), name='api_reviews_create'),
]
