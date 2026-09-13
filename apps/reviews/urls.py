"""reviews URL patterns."""
from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('request/<int:request_pk>/review/', views.submit_review, name='submit_review'),
    path('provider/<int:provider_pk>/', views.provider_reviews, name='provider_reviews'),
]
