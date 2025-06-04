from rest_framework import serializers
from .models import (
    UserProfile, UserCSV, CSVHeading, CSVValue,
    Dashboard
)

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['', 'username', 'created_at']


class UserCSVSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCSV
        fields = '__all__'


class CSVHeadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CSVHeading
        fields = '__all__'


class CSVValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = CSVValue
        fields = '__all__'


class DashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dashboard
        fields = '__all__'
