"""
ai_assistant/models.py — AI conversation and message history.
"""
from django.db import models
from apps.accounts.models import User


class AIConversation(models.Model):
    """
    A conversation session between a user and the AI assistant.
    Contains the problem context and location for that session.
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='ai_conversations'
    )
    session_title = models.CharField(max_length=200, blank=True)
    problem_context = models.TextField(blank=True)
    location_context = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation #{self.pk} — {self.user.username}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'AI Conversation'
        verbose_name_plural = 'AI Conversations'


class AIMessage(models.Model):
    """A single message in an AI conversation (either from user or AI)."""

    class Role(models.TextChoices):
        USER = 'user', 'User'
        ASSISTANT = 'assistant', 'Assistant'
        SYSTEM = 'system', 'System'

    conversation = models.ForeignKey(
        AIConversation, on_delete=models.CASCADE, related_name='messages'
    )
    role = models.CharField(max_length=20, choices=Role.choices)
    content = models.TextField()
    raw_context = models.TextField(blank=True, help_text="RAG context used to generate this message")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.role.upper()}] {self.content[:80]}"

    class Meta:
        ordering = ['created_at']
        verbose_name = 'AI Message'
        verbose_name_plural = 'AI Messages'
