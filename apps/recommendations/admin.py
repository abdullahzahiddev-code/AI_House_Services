"""recommendations/admin.py"""
from django.contrib import admin
from .models import Recommendation


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'provider', 'rank', 'score', 'created_at')
    list_filter = ('rank',)
    search_fields = ('provider__business_name', 'conversation__user__username')
