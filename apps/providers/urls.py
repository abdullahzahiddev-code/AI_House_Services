"""providers URL patterns."""
from django.urls import path
from . import views

app_name = 'providers'

urlpatterns = [
    path('', views.provider_list, name='provider_list'),
    path('<int:pk>/', views.provider_detail, name='provider_detail'),
    path('dashboard/', views.provider_dashboard, name='dashboard'),
    path('setup/', views.setup_profile, name='setup_profile'),
    path('service-areas/', views.manage_service_areas, name='manage_service_areas'),
    path('service-areas/<int:pk>/delete/', views.delete_service_area, name='delete_service_area'),
]
