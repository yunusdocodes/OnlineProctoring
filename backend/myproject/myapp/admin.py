# newapp/admin.py

from django.contrib import admin
from .models import UserProfile, Category, Performer, Feature, Testimonial, Test, TestAttempt, FAQ, AdminSettings, TestSummary, CompletedTest, UserResponse

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'address', 'avatar']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_filter = ['is_active', 'is_staff']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name', 'description']
    search_fields = ['category_name']

@admin.register(Performer)
class PerformerAdmin(admin.ModelAdmin):
    list_display = ['name', 'achievement', 'profile_picture_url']
    search_fields = ['name', 'achievement']

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']
    search_fields = ['title']

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name', 'message']
    list_filter = ['created_at']

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'created_at']
    search_fields = ['title']
    list_filter = ['category', 'created_at']

@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'test', 'score', 'completed_at']
    search_fields = ['user__username', 'test__title']
    list_filter = ['completed_at']

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question']
    search_fields = ['question']

@admin.register(AdminSettings)
class AdminSettingsAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'dark_mode', 'user_management', 'access_control',
        'system_settings', 'report_logs', 'security_settings',
        'notification_frequency', 'email_notifications'
    )
    search_fields = (
        'user_management', 'access_control', 'system_settings',
        'report_logs', 'security_settings', 'notification_frequency'
    )
    list_filter = ('dark_mode', 'email_notifications')

    # Optional: Customize the form layout
    fieldsets = (
        (None, {
            'fields': (
                'dark_mode', 'user_management', 'access_control',
                'system_settings', 'report_logs', 'security_settings',
                'notification_frequency', 'email_notifications'
            )
        }),
    )

@admin.register(TestSummary)
class TestSummaryAdmin(admin.ModelAdmin):
    list_display = ('title', 'average_score', 'total_users', 'median_score', 'pass_rate', 'total_attempts')
    search_fields = ('title',)
    list_filter = ('pass_rate',)

@admin.register(CompletedTest)
class CompletedTestAdmin(admin.ModelAdmin):
    list_display = ('get_user_name', 'get_user_email', 'title', 'highest_score', 'time_taken')
    search_fields = ('user__username', 'user__email', 'title')  # Use double underscore to access related fields
    list_filter = ('highest_score',)

    def get_user_name(self, obj):
        return obj.user.username  # Accessing the username from the User model
    get_user_name.short_description = 'User  Name'  # Set a user-friendly name for the column

    def get_user_email(self, obj):
        return obj.user.email  # Accessing the email from the User model
    get_user_email.short_description = 'User  Email'  # Set a user-friendly name for the column

class UserResponseAdmin(admin.ModelAdmin):
    # Specify the fields to display in the admin list view
    list_display = ('test_name', 'question', 'correct', 'incorrect', 'attempts')
    
    # Specify the default ordering of the list view
    ordering = ('test_name',)  # You can change this to any field you prefer
    
    # Specify the fields to filter by in the admin list view
    list_filter = ('test_name',)  # You can add more fields if needed

    # Optionally, you can add search functionality
    search_fields = ('test_name', 'question')  # Allows searching by test name and question

# Register the UserResponse model with the UserResponseAdmin configuration
admin.site.register(UserResponse, UserResponseAdmin)