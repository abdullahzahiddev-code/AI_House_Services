"""services URL patterns."""
from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('request/new/', views.create_request, name='create_request'),
    path('my-requests/', views.my_requests, name='my_requests'),
    path('request/<int:pk>/', views.request_detail, name='request_detail'),
    path('request/<int:pk>/status/', views.update_request_status, name='update_status'),
    path('request/<int:pk>/cancel/', views.cancel_request, name='cancel_request'),
]
