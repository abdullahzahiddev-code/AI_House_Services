"""recommendations/models.py — Provider recommendations linked to AI conversations."""
from django.db import models
from apps.ai_assistant.models import AIConversation
from apps.providers.models import ProviderProfile


class Recommendation(models.Model):
    """
    Stores a recommended provider for an AI conversation.
    Keeps a record of why the provider was recommended and what score they received.
    """
    conversation = models.ForeignKey(
        AIConversation, on_delete=models.CASCADE, related_name='recommendations'
    )
    provider = models.ForeignKey(
        ProviderProfile, on_delete=models.CASCADE, related_name='recommendations_received'
    )
    rank = models.PositiveSmallIntegerField(default=1)
    score = models.FloatField(default=0.0)
    reason = models.TextField(blank=True)
    was_contacted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommendation #{self.rank}: {self.provider.business_name} (score: {self.score:.2f})"

    class Meta:
        ordering = ['rank']
        verbose_name = 'Recommendation'
        verbose_name_plural = 'Recommendations'
