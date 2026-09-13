"""services/admin.py"""
from django.contrib import admin
from .models import ServiceRequest


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'provider', 'category', 'status', 'location', 'created_at')
    list_filter = ('status', 'category', 'ai_recommended')
    search_fields = ('customer__username', 'provider__business_name', 'problem_description')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
