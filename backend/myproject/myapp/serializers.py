from rest_framework import serializers
from .models import (
    UserProfile, Category, Performer, Feature, Testimonial, 
    Test, TestAttempt, FAQ, TestSettings, AdminSettings, 
    TestSummary, CompletedTest, UserResponse
)
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'phone_number', 'address', 'avatar']
        read_only_fields = ['id', 'username']  # Make id and username read-only

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "Passwords do not match."})
        return attrs

# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'category_name', 'description']

# Performer Serializer
class PerformerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performer
        fields = ['id', 'name', 'achievement', 'profile_picture_url', 'biography']

# Feature Serializer
class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ['id', 'title', 'description']

# Testimonial Serializer
class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ['id', 'name', 'message', 'profile_picture_url', 'created_at']

# Test Serializer
class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ['id', 'title', 'description', 'category', 'created_at']

# Test Attempt Serializer
class TestAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestAttempt
        fields = ['id', 'user', 'test', 'score', 'completed_at']

# FAQ Serializer
class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer']

# TestSettings Serializer
class TestSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestSettings
        fields = '__all__'

# Login Serializer for JWT Authentication
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(required=True, write_only=True, max_length=128)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)

        if user is None:
            raise ValidationError("Invalid credentials.")

        data["user"] = user  # Attach the authenticated user to the validated data
        return data

# Token Serializer for JWT Authentication (used for generating tokens)
class TokenSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

class AdminSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminSettings
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = '__all__'

class TestAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestAttempt
        fields = '__all__'

class TestSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = TestSummary
        fields = '__all__'

class CompletedTestSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = CompletedTest
        fields = ['id', 'user_email', 'user_name', 'title', 'highest_score', 'time_taken']
        read_only_fields = ['user_email', 'user_name']  # These fields are read-only

class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserResponse
        fields = ['test_name', 'question', 'correct', 'incorrect', 'attempts']