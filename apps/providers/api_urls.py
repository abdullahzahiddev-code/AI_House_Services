"""providers REST API URLs."""
from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.ProviderListAPIView.as_view(), name='api_provider_list'),
    path('<int:pk>/', api_views.ProviderDetailAPIView.as_view(), name='api_provider_detail'),
    path('me/', api_views.MyProviderProfileAPIView.as_view(), name='api_provider_me'),
    path('categories/', api_views.ServiceCategoryListAPIView.as_view(), name='api_categories'),
]
