"""
providers/models.py — Service categories, provider profiles, skills, areas, availability.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.accounts.models import User


class ServiceCategory(models.Model):
    """
    E.g. Plumber, Electrician, AC Technician, Carpenter, etc.
    Each category has a name, description, and icon for display.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='🔧', help_text="Emoji or icon class")
    common_problems = models.TextField(
        blank=True,
        help_text="Comma-separated list of common problems this category handles"
    )
    keywords = models.TextField(
        blank=True,
        help_text="Keywords for AI matching, comma-separated"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_keywords_list(self):
        return [k.strip() for k in self.keywords.split(',') if k.strip()]

    def get_problems_list(self):
        return [p.strip() for p in self.common_problems.split(',') if p.strip()]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Service Category'
        verbose_name_plural = 'Service Categories'
        ordering = ['name']


class Skill(models.Model):
    """Individual skills a provider can have, e.g., 'Pipe Leakage Repair'."""
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        ServiceCategory, on_delete=models.CASCADE, related_name='skills'
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    class Meta:
        ordering = ['name']


class ProviderProfile(models.Model):
    """
    A service provider's professional profile.
    This is the main model containing all information about a provider.
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='provider_profile'
    )
    business_name = models.CharField(max_length=200)
    category = models.ForeignKey(
        ServiceCategory, on_delete=models.SET_NULL,
        null=True, related_name='providers'
    )
    bio = models.TextField(blank=True)
    experience_years = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(50)],
        help_text="Years of professional experience"
    )
    skills = models.ManyToManyField(Skill, blank=True, related_name='providers')

    # Contact & Location
    phone_number = models.CharField(max_length=20, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    base_location = models.CharField(max_length=200, blank=True)

    # Pricing
    min_charge = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Minimum service charge in PKR"
    )
    max_charge = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Maximum service charge in PKR"
    )

    # Ratings (updated automatically by reviews)
    average_rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    total_reviews = models.PositiveIntegerField(default=0)
    total_jobs_completed = models.PositiveIntegerField(default=0)

    # Status
    is_verified = models.BooleanField(default=False, help_text="Admin-verified provider")
    is_available = models.BooleanField(default=True)
    profile_picture = models.ImageField(upload_to='provider_pics/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_charge_range(self):
        if self.min_charge and self.max_charge:
            return f"Rs. {self.min_charge:,.0f} – {self.max_charge:,.0f}"
        return "Contact for pricing"

    def get_skills_list(self):
        return list(self.skills.values_list('name', flat=True))

    def get_service_areas_list(self):
        return list(self.service_areas.values_list('area_name', flat=True))

    def __str__(self):
        return f"{self.business_name} ({self.category})"

    class Meta:
        verbose_name = 'Provider Profile'
        verbose_name_plural = 'Provider Profiles'
        ordering = ['-average_rating', '-experience_years']


class ServiceArea(models.Model):
    """Areas/locations that a provider serves."""
    provider = models.ForeignKey(
        ProviderProfile, on_delete=models.CASCADE, related_name='service_areas'
    )
    area_name = models.CharField(max_length=200)
    city = models.CharField(max_length=100, default='Rawalpindi')

    def __str__(self):
        return f"{self.area_name}, {self.city}"

    class Meta:
        verbose_name = 'Service Area'
        verbose_name_plural = 'Service Areas'
        ordering = ['area_name']


class Availability(models.Model):
    """When a provider is available to work."""

    class Day(models.TextChoices):
        MONDAY = 'MON', 'Monday'
        TUESDAY = 'TUE', 'Tuesday'
        WEDNESDAY = 'WED', 'Wednesday'
        THURSDAY = 'THU', 'Thursday'
        FRIDAY = 'FRI', 'Friday'
        SATURDAY = 'SAT', 'Saturday'
        SUNDAY = 'SUN', 'Sunday'

    provider = models.ForeignKey(
        ProviderProfile, on_delete=models.CASCADE, related_name='availability'
    )
    day = models.CharField(max_length=3, choices=Day.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.provider.business_name} — {self.day} {self.start_time}-{self.end_time}"

    class Meta:
        verbose_name = 'Availability'
        verbose_name_plural = 'Availabilities'
        unique_together = ('provider', 'day')
        ordering = ['day']
