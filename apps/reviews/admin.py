"""reviews/admin.py"""
from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'reviewer', 'provider', 'rating', 'is_verified', 'created_at')
    list_filter = ('rating', 'is_verified')
    search_fields = ('reviewer__username', 'provider__business_name', 'comment')
    list_editable = ('is_verified',)
    date_hierarchy = 'created_at'
