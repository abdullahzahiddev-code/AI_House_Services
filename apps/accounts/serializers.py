"""accounts/serializers.py — DRF serializers for API."""
from rest_framework import serializers
from .models import User, CustomerProfile


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ('location', 'full_address', 'preferred_contact')


class UserSerializer(serializers.ModelSerializer):
    customer_profile = CustomerProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'phone_number', 'role', 'profile_picture', 'customer_profile',
                  'created_at')
        read_only_fields = ('id', 'role', 'created_at')


class CustomerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)
    location = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',
                  'phone_number', 'password', 'password2', 'location')

    def validate(self, data):
        if data['password'] != data.pop('password2'):
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        location = validated_data.pop('location', '')
        user = User.objects.create_user(
            role=User.Role.CUSTOMER,
            **validated_data,
        )
        CustomerProfile.objects.create(user=user, location=location)
        return user


class ProviderRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',
                  'phone_number', 'password', 'password2')

    def validate(self, data):
        if data['password'] != data.pop('password2'):
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            role=User.Role.PROVIDER,
            **validated_data,
        )
        return user
