"""services REST API URLs."""
from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.ServiceRequestListCreateAPIView.as_view(), name='api_requests'),
    path('<int:pk>/', api_views.ServiceRequestDetailAPIView.as_view(), name='api_request_detail'),
]
