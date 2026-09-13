"""services/serializers.py"""
from rest_framework import serializers
from .models import ServiceRequest


class ServiceRequestSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    provider_name = serializers.CharField(source='provider.business_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = ServiceRequest
        fields = (
            'id', 'customer_name', 'provider_name', 'category_name',
            'problem_description', 'location', 'preferred_date',
            'preferred_time', 'status', 'provider_notes',
            'estimated_cost', 'ai_recommended', 'created_at',
        )
        read_only_fields = ('id', 'customer_name', 'created_at')


class ServiceRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        fields = (
            'category', 'problem_description', 'location',
            'preferred_date', 'preferred_time',
        )

    def create(self, validated_data):
        validated_data['customer'] = self.context['request'].user
        return super().create(validated_data)
