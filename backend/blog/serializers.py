from rest_framework import serializers
from .models import Test, Question, TestAttempt, UserAnswer
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from urllib.parse import quote
from .models import (
    UserProfile,CustomUser,UserPerformance,Review,Category,StudentCapture,RecentActivity,AllowedParticipant,Answer,Option,Question, UserSettings,AdminSettings, ManageTests,UserResponse,
 ActivityLog,Performer,Enrollment,TestUser,TestResult,TestAttempt,Feature, LeaderboardEntry,
 Testimonial,Test, Announcement, FAQ, PasswordReset, ContactMessage,AdminNotification, Notification,AttemptedTest,Achievement,
PerformanceStat,CompletedTest, TestSummary, TestParticipant
)
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import MalpracticeLog


User = get_user_model()
class RegisterSerializer(serializers.ModelSerializer):
    role = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'full_name', 'role']
        extra_kwargs = {'password': {'write_only': True},    'full_name': {'read_only': True},}

    def create(self, validated_data):
        full_name = f"{validated_data.get('first_name', '')} {validated_data.get('last_name', '')}".strip()
        # Use create_user to hash password and save user
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            full_name=full_name,
            role=validated_data['role']
        )
        return user
    
from rest_framework import serializers
from .models import TestParticipant

class TestParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestParticipant
        fields = '__all__'

class TestSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttemptedTest
        fields = ['test', 'score']
class ReviewAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['question', 'answer', 'is_correct']
class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser 
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile_picture', 'phone', 'linkedin', 'status']

class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ['user', 'action', 'date', 'ip']
class ReviewSerializer(serializers.ModelSerializer):
    answers = ReviewAnswerSerializer(many=True, source='answers')

    class Meta:
        model = TestAttempt
        fields = ['id', 'test', 'answers']
class AttemptedTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttemptedTest
        fields = '__all__'
        
class PerformanceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPerformance
        fields = ['total_tests', 'total_score']
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'
class TestResultSerializer(serializers.ModelSerializer):
    correct_answer = serializers.CharField(required=True)
    class Meta:
        model = TestResult
        fields = '__all__'

from .models import Feedback
class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'
class LeaderboardEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaderboardEntry
        fields = '__all__'

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id','title', 'message', 'created_by']  # Add relevant fields

class NotificationSerializer(serializers.ModelSerializer):
    announcement = AnnouncementSerializer()  # Nest announcement details

    class Meta:
        model = Notification
        fields = ['id', 'is_read', 'created_at', 'announcement']
class UserSettingsSerializer(serializers.ModelSerializer):
   class Meta:
      model = UserSettings
      fields = ['dark_mode', 'test_access', 'integration', 'auto_save', 'time_reminder', 'notifications']

class UserProfileSerializer(serializers.ModelSerializer):
   username = serializers.CharField(source='user.username', read_only=True)
   class Meta:
      model = UserProfile
      fields = ['id', 'username', 'name', 'phone_number', 'address', 'profile_picture_url','bio',]

class CategorySerializer(serializers.ModelSerializer):
   class Meta:
      model = Category
      fields = '__all__'

class OptionSerializer(serializers.ModelSerializer):
   class Meta:
      model = Option
      fields = ["id", "option_text"]

class AdminSettingsSerializer(serializers.ModelSerializer):
 class Meta:
    model = AdminSettings
    fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
 class Meta:
    model = Review
    fields = ['question', 'answer', 'correct']

class ManageTestsSerializer(serializers.ModelSerializer):
   class Meta:
      model = ManageTests
      fields = '__all__'

class UserResponseSerializer(serializers.ModelSerializer):
   class Meta:
      model = UserResponse
      fields = '__all__'

class PerformerSerializer(serializers.ModelSerializer):
   class Meta:
      model = Performer
      fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
   class Meta:
      model = Review
      fields = ['question', 'answer', 'correct']
class FeatureSerializer(serializers.ModelSerializer):
 class Meta:
    model = Feature 
    fields = '__all__'

class TestimonialSerializer(serializers.ModelSerializer):
 class Meta:
    model = Testimonial
    fields = '__all__'


class FAQSerializer(serializers.ModelSerializer):
   class Meta:
      model = FAQ
      fields = '__all__'

class PasswordResetSerializer(serializers.ModelSerializer):
   class Meta:
      model = PasswordReset
      fields = '__all__'

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = "__all__"

class AdminNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminNotification
        fields = "__all__"

class AchievementSerializer(serializers.ModelSerializer):
   class Meta:
      model = Achievement
      fields = '__all__'

class TopScorerSerializer(serializers.Serializer):
 studentId = serializers.IntegerField(source="student.id")
 averageScore = serializers.FloatField()

class ActivitySerializer(serializers.ModelSerializer):
   class Meta:
      model = ActivityLog
      fields = ['activity', 'timestamp']

class TestSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = TestSummary
        fields = '__all__'

class CompletedTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompletedTest
        fields = "__all__"

class PerformanceStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceStat
        fields = '__all__'

class RecentActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecentActivity
        fields = fields = ['id', 'user', 'description', 'details', 'timestamp']
class AllowedParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllowedParticipant
        fields = ['test', 'email']
class TestUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestUser
        fields = ['id', 'name', 'email', 'created_at']
class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserResponse
        fields = ['test_name', 'question', 'correct', 'incorrect', 'attempts']
   
class QuestionSerializer(serializers.ModelSerializer):
    test = serializers.PrimaryKeyRelatedField(queryset=Test.objects.all())
    options = serializers.JSONField(default=list)
    correct_answer = serializers.JSONField(default=list)

    class Meta:
        model = Question
        fields = ["id", "text", "type", "options", "correct_answer", "test"]

    def create(self, validated_data):
        test = validated_data.get('test', None)
        question = Question.objects.create( **validated_data)
        return question

    def to_representation(self, instance):
        data = super().to_representation(instance)
        question_type = data.get("type")
        correct_answer = data.get("correct_answer")
        options = data.get("options", [])

        # Ensure correct_answer is a list (normalize)
        if not isinstance(correct_answer, list):
            correct_answer = [correct_answer]

        # Handle multiplechoice (store index)
        if question_type == "multiplechoice":
            try:
                correct_option = correct_answer[0]
                if isinstance(correct_option, int):
                    # correct_answer is already index
                    data["correctAnswer"] = correct_option
                elif isinstance(correct_option, str):
                    data["correctAnswer"] = options.index(correct_option)
                else:
                    data["correctAnswer"] = -1
            except Exception:
                data["correctAnswer"] = -1

        elif question_type == "multipleresponse":
            data["correctAnswers"] = correct_answer

        elif question_type == "truefalse":
            value = correct_answer[0] if correct_answer else False
            data["correctAnswer"] = bool(value)

        elif question_type == "fillintheblank":
            data["correctAnswer"] = correct_answer[0] if correct_answer else ""

        return data



class MalpracticeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MalpracticeLog
        fields = '__all__'

from .models import AllowedParticipant
from .utils import encode_testid_to_secure_uuid, send_test_invite_emails

class TestSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.get_full_name", read_only=True)
    questions = serializers.SerializerMethodField()
    allowed_emails = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = Test
        fields = '__all__'
        read_only_fields = ['owner']

    def get_questions(self, obj):
        """Return all related manual questions (if any)."""
        return QuestionSerializer(obj.questions.all(), many=True).data

    def create(self, validated_data):
        request = self.context.get("request")
        questions_data = request.data.get('questions', [])  # ← get from raw data
        allowed_emails = validated_data.pop('allowed_emails', [])

        test = Test.objects.create(owner=request.user, **validated_data)

        # ✅ Create manual questions if any
        for question_data in questions_data:
            Question.objects.create(test=test, **question_data)

        test.update_totals()

        # ✅ Save and send invites for protected tests
        if test.access_type == "protected" and allowed_emails:
            AllowedParticipant.objects.bulk_create([
                AllowedParticipant(test=test, email=email.lower()) for email in allowed_emails
            ])
            secure_uuid = encode_testid_to_secure_uuid(test.id)
            test_link = f"http://localhost:3000/smartbridge/online-test-assessment/{secure_uuid}"
            send_test_invite_emails(allowed_emails, test_link)

        return test

    def update(self, instance, validated_data):
        request = self.context.get("request")
        questions_data = request.data.get('questions', [])
        allowed_emails = validated_data.pop('allowed_emails', [])

        if questions_data:
            instance.questions.all().delete()
            for question_data in questions_data:
                Question.objects.create(test=instance, **question_data)

        instance.marks_per_question = validated_data.get('marks_per_question', instance.marks_per_question)
        instance.time_limit_per_question = validated_data.get('time_limit_per_question', instance.time_limit_per_question)

        instance.total_questions = instance.questions.count()
        instance.total_marks = instance.total_questions * float(instance.marks_per_question)
        instance.total_time_limit = instance.total_questions * float(instance.time_limit_per_question)

        instance.save()

        if instance.access_type == "protected" and allowed_emails:
            AllowedParticipant.objects.filter(test=instance).delete()
            AllowedParticipant.objects.bulk_create([
                AllowedParticipant(test=instance, email=email.lower()) for email in allowed_emails
            ])
            secure_uuid = encode_testid_to_secure_uuid(instance.id)
            test_link = f"http://localhost:3000/smartbridge/online-test-assessment/{secure_uuid}"
            send_test_invite_emails(allowed_emails, test_link)

        return instance

class UserAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source="question.text", read_only=True)

    class Meta:
        model = UserAnswer
        fields = ['id', 'question_text', 'selected_option']

class StudentCaptureSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCapture
        fields = '__all__'
        read_only_fields = ('timestamp', 'is_valid', 'validation_message')

class TestParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestParticipant
        fields = ['test', 'name', 'email']

class TestAttemptSerializer(serializers.ModelSerializer):
    test_name = serializers.CharField(source="test.title", read_only=True)
    subject = serializers.CharField(source="test.subject", read_only=True)
      
    answers = UserAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = TestAttempt
        fields = "__all__" 
        extra_kwargs = {
            'score': {'required': False},  
            'test': {'required': True}, 
        }

class BulkQuestionSerializer(serializers.Serializer):
     questions = QuestionSerializer(many=True)

from rest_framework import serializers
from blog.models import TestAttempt, TestParticipant  # adjust if in another app

class TestAttemptResultSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    time_taken = serializers.SerializerMethodField()
    passed = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()  # ⬅️ New

    class Meta:
        model = TestAttempt
        fields = [
            'id',
            'name',
            'email',
            'score',
            'status',
            'time_taken',
            'rank',
            'accuracy',
            'total_questions',
            'correct_answers',
            'passed',
            'video_url',  # ⬅️ Add here
        ]

    def get_name(self, obj):
        participant = TestParticipant.objects.filter(email=obj.email, test=obj.test).first()
        return participant.name if participant else obj.email

    def get_time_taken(self, obj):
        if obj.start_time and obj.end_time:
            duration = obj.end_time - obj.start_time
            total_seconds = int(duration.total_seconds())
            minutes, seconds = divmod(total_seconds, 60)
            return f"{minutes:02}:{seconds:02}"
        return "-"

    def get_passed(self, obj):
        if obj.score is not None and obj.test.pass_criteria is not None:
            return obj.score >= obj.test.pass_criteria
        return False

    def get_video_url(self, obj):
        
        request = self.context.get("request")
        participant = TestParticipant.objects.filter(email=obj.email, test=obj.test).first()
        name = participant.name if participant else obj.email
        if not name or not obj.test_id:
            return None

        encoded_name = quote(name.replace(" ", "_"))
        return request.build_absolute_uri(
            f"/api/protected-video/?name={encoded_name}&test_id={obj.test_id}"
        )
