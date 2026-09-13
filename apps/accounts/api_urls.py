"""accounts REST API URLs (JWT auth)."""
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import api_views

urlpatterns = [
    path('register/customer/', api_views.CustomerRegisterAPIView.as_view(), name='api_register_customer'),
    path('register/provider/', api_views.ProviderRegisterAPIView.as_view(), name='api_register_provider'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', api_views.CurrentUserAPIView.as_view(), name='api_me'),
]
