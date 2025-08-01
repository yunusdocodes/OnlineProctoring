from django.contrib import admin
from .models import Test, TestAttempt, UserAnswer,RecentActivity,Question

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'created_at')
    search_fields = ('title', 'subject')
    ordering = ('-created_at',)

@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', 'status', 'score', 'start_time', 'end_time')
    list_filter = ('status',)
    search_fields = ('user__username', 'test__title')
    ordering = ('-start_time',)

@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_option')
    search_fields = ('attempt__user__username', 'question__text')
    ordering = ('attempt',)

class RecentActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'description', 'details','timestamp')
    search_fields = ('description',)
    
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'text_preview', 'type', 'test')  # Display a short preview of the text
    list_filter = ('type', 'test')
    search_fields = ('text',)
    readonly_fields = ('options', 'correct_answer')  # Optional: make them read-only

    def text_preview(self, obj):
        return obj.text[:50] + ('...' if len(obj.text) > 50 else '')
    text_preview.short_description = 'Question'
    
admin.site.register(RecentActivity, RecentActivityAdmin) 
from .models import Announcement, Notification

admin.site.register(Announcement)
admin.site.register(Notification)
admin.site.register(Question)

