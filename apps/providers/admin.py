"""providers/admin.py — Admin for providers."""
from django.contrib import admin
from .models import ServiceCategory, Skill, ProviderProfile, ServiceArea, Availability


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    list_filter = ('is_active',)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)


class ServiceAreaInline(admin.TabularInline):
    model = ServiceArea
    extra = 1


class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 0


@admin.register(ProviderProfile)
class ProviderProfileAdmin(admin.ModelAdmin):
    list_display = (
        'business_name', 'category', 'base_location',
        'average_rating', 'experience_years', 'is_verified', 'is_available'
    )
    list_filter = ('category', 'is_verified', 'is_available')
    search_fields = ('business_name', 'user__username', 'user__email', 'base_location')
    list_editable = ('is_verified', 'is_available')
    inlines = [ServiceAreaInline, AvailabilityInline]

    actions = ['verify_providers', 'unverify_providers']

    def verify_providers(self, request, queryset):
        count = queryset.update(is_verified=True)
        self.message_user(request, f"{count} provider(s) verified.")
    verify_providers.short_description = "✅ Verify selected providers"

    def unverify_providers(self, request, queryset):
        count = queryset.update(is_verified=False)
        self.message_user(request, f"{count} provider(s) un-verified.")
    unverify_providers.short_description = "❌ Un-verify selected providers"
