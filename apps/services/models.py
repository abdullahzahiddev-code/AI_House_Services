"""
services/models.py — Service requests (customer asking for a provider's help).
"""
from django.db import models
from apps.accounts.models import User
from apps.providers.models import ProviderProfile, ServiceCategory


class ServiceRequest(models.Model):
    """
    A customer's request for a home service.
    Lifecycle: PENDING → ACCEPTED → IN_PROGRESS → COMPLETED / REJECTED / CANCELLED
    """

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        REJECTED = 'REJECTED', 'Rejected'
        CANCELLED = 'CANCELLED', 'Cancelled'

    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='service_requests'
    )
    provider = models.ForeignKey(
        ProviderProfile, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='service_requests'
    )
    category = models.ForeignKey(
        ServiceCategory, on_delete=models.SET_NULL, null=True, blank=True
    )

    problem_description = models.TextField(
        help_text="Detailed description of the home problem"
    )
    location = models.CharField(max_length=200)
    preferred_date = models.DateField(null=True, blank=True)
    preferred_time = models.TimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    provider_notes = models.TextField(blank=True, help_text="Provider's notes or response")
    estimated_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    # AI-generated
    ai_recommended = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def can_review(self):
        """A customer can only review after service is completed."""
        return self.status == self.Status.COMPLETED

    def __str__(self):
        return f"Request #{self.pk} — {self.customer.username} — {self.category}"

    class Meta:
        verbose_name = 'Service Request'
        verbose_name_plural = 'Service Requests'
        ordering = ['-created_at']
