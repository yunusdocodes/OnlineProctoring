from django.db import models
from django.contrib.auth.models import AbstractUser , Group, Permission
from django.contrib.auth import get_user_model

class UserProfile(AbstractUser ):
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    # Specify related_name to avoid clashes
    groups = models.ManyToManyField(
        Group,
        related_name='user_profiles',  # Change this to avoid clash
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='user_profiles',  # Change this to avoid clash
        blank=True,
    )

    def __str__(self):
        return self.username  # Return the username for better representation in admin
class Category(models.Model):
    category_name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.category_name

class Performer(models.Model):
    name = models.CharField(max_length=255)
    achievement = models.CharField(max_length=255)
    profile_picture_url = models.URLField()
    biography = models.TextField()

    def __str__(self):
        return self.name

class Feature(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title

class Testimonial(models.Model):
    name = models.CharField(max_length=255)
    message = models.TextField()
    profile_picture_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Testimonial by {self.name}"

class Test(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, related_name="tests", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class TestAttempt(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)  # Use UserProfile instead of User
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.FloatField()
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.test.title} ({self.score}%)"

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        return self.question

class TestSettings(models.Model):
    test = models.OneToOneField(Test, on_delete=models.CASCADE, related_name='settings')
    is_timed = models.BooleanField(default=True)  # Test has a time limit or not
    duration = models.PositiveIntegerField(default=30)  # Duration in minutes
    allow_retakes = models.BooleanField(default=False)  # Whether the test allows retakes
    allow_question_skipping = models.BooleanField(default=True)  # Whether users can skip questions
    answer_review = models.BooleanField(default=False)  # Whether users can review answers before submission
    accessibility_options = models.BooleanField(default=False)  # Special accessibility options for disabled users
    proctoring = models.BooleanField(default=False)  # Whether the test has proctoring (monitoring)
    scoring = models.CharField(max_length=10, choices=[('auto', 'Auto'), ('manual', 'Manual')], default='auto')  # Scoring method

    def __str__(self):
        return f"Settings for {self.test.title}"

class AdminSettings(models.Model):
    dark_mode = models.BooleanField(default=False)
    user_management = models.CharField(max_length=255, default="Manage Users")
    access_control = models.CharField(max_length=255, default="Set Permissions")
    system_settings = models.CharField(max_length=255, default="Update Config")
    report_logs = models.CharField(max_length=255, default="Generate Reports")
    security_settings = models.CharField(max_length=255, default="Configure Policies")
    notification_frequency = models.CharField(max_length=255, default="Instant")
    email_notifications = models.BooleanField(default=True)

    def __str__(self):
        return f"AdminSettings(id={self.id})"
    
User  = get_user_model()

class TestSummary(models.Model):
    title = models.CharField(max_length=255)
    average_score = models.FloatField()
    total_users = models.IntegerField()
    median_score = models.FloatField()  # Added median score
    pass_rate = models.FloatField()     # Added pass rate
    total_attempts = models.IntegerField()  # Added total attempts

    def __str__(self):
        return self.title

User  = get_user_model()

class CompletedTest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    highest_score = models.FloatField()
    time_taken = models.CharField(max_length=100)  # Store time taken as a string

    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
class UserResponse(models.Model):
    test_name = models.CharField(max_length=255)
    question = models.TextField()
    correct = models.BooleanField()
    incorrect = models.BooleanField()
    attempts = models.IntegerField()

    def __str__(self):
        return f"{self.test_name} - {self.question}"