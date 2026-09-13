"""ai_assistant/admin.py"""
from django.contrib import admin
from .models import AIConversation, AIMessage


class AIMessageInline(admin.TabularInline):
    model = AIMessage
    extra = 0
    readonly_fields = ('role', 'content', 'created_at')


@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_title', 'location_context', 'created_at')
    search_fields = ('user__username', 'session_title', 'problem_context')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [AIMessageInline]
    date_hierarchy = 'created_at'
