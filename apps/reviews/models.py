"""
reviews/models.py — Customer ratings and reviews for providers.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg
from apps.accounts.models import User
from apps.providers.models import ProviderProfile
from apps.services.models import ServiceRequest


class Review(models.Model):
    """
    A customer's review of a provider after a completed service.
    Each service request can only be reviewed once.
    """
    service_request = models.OneToOneField(
        ServiceRequest, on_delete=models.CASCADE, related_name='review'
    )
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews_given'
    )
    provider = models.ForeignKey(
        ProviderProfile, on_delete=models.CASCADE, related_name='reviews'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 (worst) to 5 (best)"
    )
    comment = models.TextField(blank=True)
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update provider's average rating after each new review
        self._update_provider_rating()

    def _update_provider_rating(self):
        provider = self.provider
        stats = Review.objects.filter(
            provider=provider, is_verified=True
        ).aggregate(avg=Avg('rating'), count=models.Count('id'))
        provider.average_rating = stats['avg'] or 0.0
        provider.total_reviews = stats['count']
        provider.save(update_fields=['average_rating', 'total_reviews'])

    def __str__(self):
        return f"Review by {self.reviewer.username} → {self.provider.business_name} ({self.rating}★)"

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
