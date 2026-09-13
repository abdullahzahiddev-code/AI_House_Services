"""
accounts/models.py — Custom User model and user profiles.

We extend Django's AbstractUser so we can add a 'role' field.
Every user is either a CUSTOMER, PROVIDER, or ADMIN.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom user model with role-based access."""

    class Role(models.TextChoices):
        CUSTOMER = 'CUSTOMER', _('Customer')
        PROVIDER = 'PROVIDER', _('Service Provider')
        ADMIN = 'ADMIN', _('Admin')

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )
    phone_number = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/', blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    def is_provider(self):
        return self.role == self.Role.PROVIDER

    def is_admin_user(self):
        return self.role == self.Role.ADMIN or self.is_staff

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class CustomerProfile(models.Model):
    """Extra information for customer users."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='customer_profile'
    )
    location = models.CharField(max_length=200, blank=True, help_text="City or area")
    full_address = models.TextField(blank=True)
    preferred_contact = models.CharField(
        max_length=20,
        choices=[('phone', 'Phone'), ('email', 'Email'), ('whatsapp', 'WhatsApp')],
        default='phone',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Customer: {self.user.get_full_name() or self.user.username}"

    class Meta:
        verbose_name = 'Customer Profile'
        verbose_name_plural = 'Customer Profiles'
