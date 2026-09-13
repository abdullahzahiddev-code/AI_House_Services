"""providers/serializers.py — DRF serializers."""
from rest_framework import serializers
from .models import ProviderProfile, ServiceCategory, ServiceArea, Skill, Availability


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ('id', 'name', 'slug', 'description', 'icon', 'common_problems')


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ('id', 'name', 'category')


class ServiceAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceArea
        fields = ('id', 'area_name', 'city')


class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = ('id', 'day', 'start_time', 'end_time', 'is_available')


class ProviderProfileSerializer(serializers.ModelSerializer):
    category = ServiceCategorySerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    service_areas = ServiceAreaSerializer(many=True, read_only=True)
    availability = AvailabilitySerializer(many=True, read_only=True)
    charge_range = serializers.SerializerMethodField()
    provider_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = ProviderProfile
        fields = (
            'id', 'provider_name', 'business_name', 'category',
            'bio', 'experience_years', 'skills', 'service_areas',
            'availability', 'average_rating', 'total_reviews',
            'total_jobs_completed', 'base_location',
            'min_charge', 'max_charge', 'charge_range',
            'is_verified', 'is_available', 'profile_picture',
        )

    def get_charge_range(self, obj):
        return obj.get_charge_range()


class ProviderProfileUpdateSerializer(serializers.ModelSerializer):
    """For providers to update their own profile."""
    class Meta:
        model = ProviderProfile
        fields = (
            'business_name', 'category', 'bio', 'experience_years',
            'skills', 'phone_number', 'whatsapp_number', 'email',
            'base_location', 'min_charge', 'max_charge', 'is_available',
        )
