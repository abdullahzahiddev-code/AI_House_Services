"""reviews/serializers.py"""
from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewer.get_full_name', read_only=True)
    provider_name = serializers.CharField(source='provider.business_name', read_only=True)

    class Meta:
        model = Review
        fields = (
            'id', 'reviewer_name', 'provider_name', 'rating',
            'comment', 'created_at',
        )
        read_only_fields = ('id', 'reviewer_name', 'provider_name', 'created_at')


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('service_request', 'rating', 'comment')

    def validate_service_request(self, value):
        if value.customer != self.context['request'].user:
            raise serializers.ValidationError("You can only review your own service requests.")
        if value.status != 'COMPLETED':
            raise serializers.ValidationError("You can only review completed services.")
        if hasattr(value, 'review'):
            raise serializers.ValidationError("This service has already been reviewed.")
        return value

    def create(self, validated_data):
        service_request = validated_data['service_request']
        validated_data['reviewer'] = self.context['request'].user
        validated_data['provider'] = service_request.provider
        return super().create(validated_data)
