from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
import io
import os
import cv2
import subprocess
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import PyPDF2
import csv
import tempfile
from blog.utils import send_congratulations_email
from datetime import datetime
from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Max, Sum, Count
from rest_framework.decorators import api_view,permission_classes, action, parser_classes
from rest_framework.permissions import IsAuthenticated,AllowAny, IsAdminUser
from .models import Test, Question, TestAttempt, UserAnswer, Answer
from .serializers import TestAttemptResultSerializer,TestSerializer, QuestionSerializer, TestAttemptSerializer, UserAnswerSerializer,ReviewAnswerSerializer,ReviewSerializer
from django.utils import timezone
from django.db.models import Count, Avg, Max
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework import generics, viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.http import FileResponse
from django.contrib.auth import update_session_auth_hash
import secrets
from django.contrib.auth.decorators import login_required
import json
from rest_framework.exceptions import NotAuthenticated
from reportlab.pdfgen import canvas
from .models import (Category,TestUser,AllowedParticipant,save_completed_test,CustomUser,Enrollment,Test,LeaderboardEntry,TestAttempt,ManageTests,Learner,Assessment,UserSettings,
TestResult,Question,UserResponse,UserProfile,AdminSettings,RecentActivity,Announcement, Test, TestParticipant,
Performer,Feature,ActivityLog,Testimonial,FAQ,Feedback,PasswordReset,ContactMessage,AdminNotification,
UserToken,Notification,AttemptedTest,Achievement,PerformanceStat,CompletedTest,TestSummary,PerformanceHistory, MalpracticeLog
)
from .serializers import (
CategorySerializer,
TestUserSerializer,
ActivityLogSerializer,
RecentActivitySerializer,
BulkQuestionSerializer,
TestSerializer,ContactMessageSerializer,AdminNotificationSerializer,
EnrollmentSerializer,
PerformanceHistorySerializer,
LeaderboardEntrySerializer,
TestAttemptSerializer,
TestSubmissionSerializer,
UserSettingsSerializer,
AnnouncementSerializer,
ManageTestsSerializer,
QuestionSerializer,
UserResponseSerializer,
UserProfileSerializer,
AttemptedTestSerializer,
AdminSettingsSerializer,
PerformerSerializer,
UserSerializer,
RegisterSerializer,
FeatureSerializer,
TestimonialSerializer,
FAQSerializer,
PasswordResetSerializer,
ReviewSerializer,
NotificationSerializer,
AchievementSerializer,
PerformanceStatSerializer,
CompletedTestSerializer,
TestSummarySerializer,
FeedbackSerializer,
MalpracticeLogSerializer
)
from rest_framework import generics
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes
from .serializers import UserSerializer
from django.core.cache import cache
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from .utils import generate_otp, send_otp_email
from django.middleware.csrf import get_token
from .utils import encode_testid_to_secure_uuid,decode_secure_uuid_to_testid
from django.contrib.auth import get_user_model

def get_secure_uuid(request, testid):
    uuid_str = encode_testid_to_secure_uuid(int(testid))
    return JsonResponse({"encoded_uuid": uuid_str})

@api_view(['POST'])
def request_otp(request):
    """API to generate and send OTP"""
    email = request.data.get('email')
   
    # Validate email input
    if not email:
        return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

    # Check if email is associated with a registered user (optional security step)
    if not CustomUser.objects.filter(email=email).exists():
        return Response({"error": "Email not found"}, status=status.HTTP_404_NOT_FOUND)

    # Generate and store OTP (valid for 10 minutes)
    otp = generate_otp()
    cache.set(email, otp, timeout=600)  

    # Send OTP email
    send_otp_email(email, otp)
   
    return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)


User = get_user_model()

import os
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.core.files.storage import default_storage
from django.conf import settings

def sanitize_filename(value):
    return "".join(c if c.isalnum() else "_" for c in value)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, JSONParser, FormParser])
def log_malpractice(request):
    try:
        user = request.user
        name = sanitize_filename(request.data.get("name") or "Unknown")
        test_id = request.data.get("test_id")
        event_type = request.data.get("event_type", "Unknown event")

        if not test_id:
            return Response({"error": "Missing test_id"}, status=400)

        # 📌 Get latest TestAttempt for user & test to calculate timestamp
        attempt = TestAttempt.objects.filter(user=user, test_id=test_id).last()
        if not attempt or not attempt.start_time:
            return Response({"error": "Test attempt not found or missing start time"}, status=404)

        elapsed = now() - attempt.start_time
        minutes, seconds = divmod(elapsed.total_seconds(), 60)
        test_timestamp = f"{int(minutes):02}:{int(seconds):02}"  # e.g., 00:47

        # 📁 Folder: media/logs/<username>_<test_id>/
        folder_path = os.path.join(settings.MEDIA_ROOT, "logs", f"{name}_{test_id}")
        os.makedirs(folder_path, exist_ok=True)

        # 📸 Save frame if provided
        if "frame" in request.FILES:
            frame = request.FILES["frame"]
            timestamp = now().strftime("%Y%m%d_%H%M%S")
            frame_name = f"frame_{timestamp}.jpg"
            frame_path = os.path.join(folder_path, frame_name)

            with open(frame_path, "wb+") as f:
                for chunk in frame.chunks():
                    f.write(chunk)

        # 📝 Append to log-malpractice.txt
        log_file_path = os.path.join(folder_path, "log-malpractice.txt")
        with open(log_file_path, "a") as log_file:
            log_file.write(f"{now().date()} | {test_timestamp} | {event_type}\n")

        return Response({
            "message": "Malpractice logged",
            "timestamp": test_timestamp
        }, status=201)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def save_proctoring_video(request):
    try:
        video = request.FILES.get("video")
        name = sanitize_filename(request.data.get("name") or "Unknown")
        test_id = request.data.get("test_id")

        if not video or not test_id:
            return Response({"error": "Missing video or test_id"}, status=400)

        # ✅ Create folder
        folder_path = os.path.join(settings.MEDIA_ROOT, "logs", f"{name}_{test_id}")
        os.makedirs(folder_path, exist_ok=True)

        # ✅ Save raw video file
        video_path = os.path.join(folder_path, "proctoring_recording.webm")
        with open(video_path, "wb+") as f:
            for chunk in video.chunks():
                f.write(chunk)

        # ✅ Apply faststart using ffmpeg
        temp_video_path = os.path.join(folder_path, "temp_proctoring_recording.webm")
        ffmpeg_path = r"D:\ffm\ffmpeg-7.1.1-essentials_build\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe"
        try:
            subprocess.run([
                ffmpeg_path,
                "-i", video_path,
                "-c", "copy",
                "-movflags", "faststart",
                temp_video_path
            ], check=True)

            # ✅ Replace original with optimized version
            os.replace(temp_video_path, video_path)

        except subprocess.CalledProcessError as ffmpeg_err:
            return Response({"error": f"FFmpeg processing failed: {ffmpeg_err}"}, status=500)

        # ✅ Log the event
        log_file = os.path.join(folder_path, "log-malpractice.txt")
        with open(log_file, "a") as log:
            log.write(f"{now()} - Proctoring video uploaded & optimized\n")

        return Response({"message": "🎥 Video saved and optimized successfully"}, status=201)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
from django.http import FileResponse

class ProtectedVideoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        name = request.query_params.get('name')
        test_id = request.query_params.get('test_id')

        if not name or not test_id:
            return Response({'error': 'Missing parameters'}, status=status.HTTP_400_BAD_REQUEST)

        relative_path = f"logs/{name}_{test_id}/proctoring_recording.webm"
        video_path = os.path.join(settings.MEDIA_ROOT, relative_path)

        if os.path.exists(video_path):
            return FileResponse(open(video_path, 'rb'), content_type='video/webm')
        else:
            return Response({'error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)
            
class TestAttemptResultViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TestAttemptResultSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        test_id = self.request.query_params.get("test_id")
        if test_id:
            return TestAttempt.objects.filter(test_id=test_id).order_by("-score")
        return TestAttempt.objects.none()

@api_view(['POST'])
def verify_otp(request):
    """API to verify OTP"""
    email = request.data.get('email')
    otp = request.data.get('otp')

    if not email or not otp:
        return Response({"error": "Email and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)

    # Retrieve OTP from cache
    stored_otp = cache.get(email)

    if stored_otp and stored_otp == otp:
        cache.delete(email)  # Remove OTP after verification
        return Response({"message": "OTP verified successfully"}, status=status.HTTP_200_OK)
    return Response({"error": "Invalid OTP or expired"}, status=status.HTTP_400_BAD_REQUEST)
@api_view(['GET'])
def user_management_stats(request):
    total_users = CustomUser.objects.count()
    active_users = CustomUser.objects.filter(is_active=True).count()
    admin_users = CustomUser.objects.filter(role="Admin").count()
    normal_users = CustomUser.objects.filter(role="User").count()

    return Response({
        "total_users": total_users,
        "active_users": active_users,
        "admin_users": admin_users,
        "normal_users": normal_users
    })

def test_completion_rate_view(request):
    # Initialize a dictionary to hold completion rates
    completion_rates = {}

    # Get all active tests
    tests = Test.objects.filter(is_active=True)

    # Calculate completion rates for each test
    for test in tests:
        # Count total attempts for the test
        total_attempts = TestAttempt.objects.filter(test=test).count()

        # Count completed attempts (passed or failed)
        completed_attempts = TestAttempt.objects.filter(test=test, status__in=['passed', 'failed']).count()

        # Calculate completion rate
        if total_attempts > 0:
            completion_rate = (completed_attempts / total_attempts) * 100
        else:
            completion_rate = 0

        # Store the completion rate in the dictionary
        completion_rates[test.subject] = completion_rate

    return JsonResponse(completion_rates)
def test_management_view(request):
    # Fetch all active tests
    tests = Test.objects.filter(is_active=True).values('id', 'title', 'subject', 'start_date')

    # Convert the queryset to a list of dictionaries
    test_list = list(tests)

    return JsonResponse(test_list, safe=False)
def test_overview_view(request):
    # Total Number of Tests
    total_tests = Test.objects.filter(is_active=True).count()

    # Average Marks per Test
    average_marks = Test.objects.aggregate(Avg('total_marks'))['total_marks__avg'] or 0

    # Maximum Score of Tests
    max_score = Test.objects.aggregate(Max('max_score'))['max_score__max'] or 0

    # List of Active Tests
    active_tests = Test.objects.filter(is_active=True).values('id', 'title', 'description', 'total_marks', 'max_score')

    # Prepare the response data
    test_data = {
        'total_tests': total_tests,
        'average_marks': average_marks,
        'max_score': max_score,
        'active_tests': list(active_tests),
    }

    return JsonResponse(test_data)
def dashboard_view(request):
    # Total Students
    total_students = CustomUser.objects.filter(is_active=True).count()

    # Total Tests
    total_tests = Test.objects.filter(is_active=True).count()

    # Average Score
    average_score = TestAttempt.objects.aggregate(Avg('score'))['score__avg'] or 0

    # Completion Rate
    total_completed_tests = TestAttempt.objects.filter(status='passed').count() + TestAttempt.objects.filter(status='failed').count()
    completion_rate = (total_completed_tests / total_tests * 100) if total_tests > 0 else 0
    
    # 🟡 Step 1: Get top scorers based on email
    raw_top_scorers = (
        TestAttempt.objects.values('email')
        .annotate(average_score=Avg('score'))
        .order_by('-average_score')[:5]
    )

    # 🟢 Step 2: Replace email with name from TestParticipant (fallback to email if name not found)
    top_scorers = []
    for scorer in raw_top_scorers:
        email = scorer['email']
        print("Checking scorer email:", email)
        participant = TestParticipant.objects.filter(email=email).order_by('-created_at').first()
        print("Found participant:", participant.name if participant else "None")
        name = participant.name if participant else email  # fallback if no match
        top_scorers.append({
            'name': name,
            'average_score': round(scorer['average_score'], 2) if scorer['average_score'] is not None else None
        })

    # Recent Activity
    recent_activity = TestAttempt.objects.order_by('-completed_at')[:5]
    recent_data = []
    for attempt in recent_activity:
        participant = TestParticipant.objects.filter(email=attempt.email, test=attempt.test).first()
        name = participant.name if participant else attempt.email
        recent_data.append({
            'name': name,
            'test': attempt.test.title,
            'score': attempt.score,
            'completed_at': attempt.completed_at
        })
    # Prepare the response data
    dashboard_data = {
            'total_students': total_students,
            'total_tests': total_tests,
            'average_score': average_score,
            'completion_rate': completion_rate,
            'top_scorers': top_scorers,
            'recent_activity': recent_data,
        }

    return JsonResponse(dashboard_data)

class CaptureImageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if 'image' not in request.FILES:
            return Response(
                {'success': False, 'message': 'No image provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            image_file = request.FILES['image']
            user = request.user

            # Create user-specific directory
            user_dir = os.path.join(settings.MEDIA_ROOT, 'captures', str(user.id))
            os.makedirs(user_dir, exist_ok=True)

            # Read image content into memory once
            image_bytes = image_file.read()

            # Save image permanently
            filename = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            file_path = os.path.join(user_dir, filename)
            default_storage.save(file_path, ContentFile(image_bytes))

            # Write image to temporary file for OpenCV
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                tmp.write(image_bytes)
                tmp_path = tmp.name

            try:
                # Load image using OpenCV
                img = cv2.imread(tmp_path)
                if img is None:
                    raise ValueError("Could not read the image file")

                # Convert to grayscale
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                # Load OpenCV face detector
                face_cascade = cv2.CascadeClassifier(
                    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                )

                # Detect faces
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(100, 100)
                )

                # Validation logic
                validation = {
                    'face_detected': len(faces) > 0,
                    'multiple_faces': len(faces) > 1,
                    'looking_straight': False,
                    'is_valid': False,
                    'message': ''
                }

                if not validation['face_detected']:
                    validation['message'] = 'No face detected'
                elif validation['multiple_faces']:
                    validation['message'] = 'Multiple faces detected'
                else:
                    # Check if face is centered
                    (x, y, w, h) = faces[0]
                    face_center_x = x + w / 2
                    img_center_x = img.shape[1] / 2

                    if abs(face_center_x - img_center_x) < img.shape[1] * 0.1:
                        validation['looking_straight'] = True
                        validation['is_valid'] = True
                        validation['message'] = 'Valid capture'
                    else:
                        validation['message'] = 'Face not centered'

                return Response({
                    'success': validation['is_valid'],
                    'message': validation['message'],
                    'validation': validation,
                    'image_url': default_storage.url(file_path),
                    'user': {
                        'id': user.id,
                        'username': user.username
                    }
                })

            finally:
                # Delete temp file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

        except Exception as e:
            return Response(
                {'success': False, 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RecentActivityDeleteView(generics.DestroyAPIView):
    queryset = RecentActivity.objects.all()
    serializer_class = RecentActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
     
def get_csrf_token(request):
    return JsonResponse({"csrfToken": get_token(request)})
@api_view(["GET"])
def get_tests(request):
    tests = Test.objects.all()
    serializer = TestSerializer(tests, many=True)
    return Response(serializer.data)
   
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Test, Question

@api_view(["POST"])
def duplicate_test(request, test_id):
    try:
        test = Test.objects.get(id=test_id)
        new_test = Test.objects.create(
            title=f"{test.title} (Copy)",
            description=test.description or "",
            instructions=test.instructions or "",
            subject=test.subject or "",
            difficulty=test.difficulty or "",
            conclusion=test.conclusion or "",
            total_time_limit=test.total_time_limit or 0,
            time_limit_per_question=test.time_limit_per_question or 1,
            marks_per_question=test.marks_per_question or 1,
            pass_criteria=test.pass_criteria or 50,
            start_date=test.start_date,
            end_date=test.end_date,
            due_time=test.due_time,
            category=test.category,
            is_proctored=test.is_proctored,
            allow_feedback=test.allow_feedback,
            allow_retakes=test.allow_retakes,
            receive_email_notifications=test.receive_email_notifications,
            notification_emails=test.notification_emails,
            is_public=test.is_public,
            owner=request.user,
            is_Duplicated=True
        )


        # Copy all questions
        questions = Question.objects.filter(test=test)
        for question in questions:
            question.pk = None  # Clone
            question.test = new_test
            question.save()

        # ✅ Generate frontend test link with UUID only
        test_link = f"http://localhost:3000/smartbridge/online-test-assessment/{new_test.test_uuid}"

        return Response({
            "message": "Test duplicated successfully!",
            "new_test_id": new_test.id,
            "test_uuid": str(new_test.test_uuid),
            "test_link": test_link
        })

    except Test.DoesNotExist:
        return Response({"error": "Test not found"}, status=404)


@api_view(["GET"])
def get_test_questions(request, test_id):
    try:
        test = Test.objects.get(id=test_id)
        questions = Question.objects.filter(test=test)
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)
    except Test.DoesNotExist:
        return Response({"error": "Test not found."}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if not user:
            # Try using email
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user_obj = User.objects.get(email=username)
                user = authenticate(username=user_obj.username, password=password)
            except:
                pass

        if user:
            # Create or get DRF token
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                "user_token": token.key,
                "role": user.role,
                "user_id": user.id,
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'User registered successfully', 'role': request.data.get('role', 'user')}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = CustomUser .objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'head', 'options']

    def get_object(self):
        # Return the current user
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        user = request.user
        current_password = request.data.get('currentPassword')
        new_password = request.data.get('newPassword')

        if user.check_password(current_password):
            user.set_password(new_password)
            user.save()
            return Response({'success': 'Password changed successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_profile_picture(self, request):
        user = self.get_object()
        profile_picture = request.FILES.get('profile_picture')
        if profile_picture:
            user.profile_picture = profile_picture
            user.save()
            return Response({"profile_picture": user.profile_picture.url}, status=200)
        return Response({"error": "No file uploaded."}, status=400)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    user = request.user
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'avatar': user.profile.avatar.url if hasattr(user, 'profile') and user.profile.avatar else None,
 }
    return Response(user_data)

class CompletedTestViewSet(viewsets.ModelViewSet):
    queryset = CompletedTest.objects.all()
    serializer_class = CompletedTestSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        # Extract data from request
        data = request.data
        data["user"] = request.user.id  # Ensure the user is correctly linked

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class TestListCreateView(generics.ListCreateAPIView):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class AttemptedTestsView(generics.ListAPIView):
    serializer_class = AttemptedTestSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return AttemptedTest.objects.filter(user=self.request.user)

class PerformanceHistoryView(APIView):
    def get(self, request):
        performance_history = PerformanceHistory.objects.all()
        serializer = PerformanceHistorySerializer(performance_history, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PerformanceHistorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # ✅ Assign the logged-in user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuestionList(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]
from rest_framework.decorators import api_view

class TestDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    permission_classes = [AllowAny]
from rest_framework.decorators import api_view
@api_view(["POST"])
def create_test(request):
    serializer = TestSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)
@api_view(["GET"])

def get_test_questions(request, long_test_id):
    test_id = int(long_test_id[-3:])
    test = get_object_or_404(Test, id=test_id)
    questions = test.questions.all()
    return Response({"test_id": test.id, "questions": list(questions.values())})

class UserSettingsView(generics.RetrieveUpdateAPIView):
    queryset = UserSettings.objects.all()
    serializer_class = UserSettingsSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated("User is not authenticated.")
        user_settings, created = UserSettings.objects.get_or_create(user=self.request.user)
        return user_settings
    def post(self, request):
        user_settings = self.get_object()
        user_settings.dark_mode = False
        user_settings.test_access = 'public'
        user_settings.integration = 'none'
        user_settings.auto_save = True
        user_settings.time_reminder = 5
        user_settings.notifications = True
        user_settings.save()
        return Response({"message": "Settings reset to default."}, status=status.HTTP_200_OK)

@api_view(["GET"])
def dashboards_overview(request):
    total_learners = Learner.objects.count()
    assessments_taken = Assessment.objects.count()

    average_score = Assessment.objects.aggregate(avg_score=Avg("score"))["avg_score"]

    completion_rate = (
        0 if assessments_taken == 0
        else (Assessment.objects.filter(completed=True).count() / assessments_taken * 100)
    )

    top_scorers = Assessment.objects.order_by("-score")[:3].values("learner__name", "score")

    recent_activity_logs = ActivityLog.objects.order_by("-timestamp")[:5].values("details", "timestamp", "learner__name")

    data = {
        "total_learners": total_learners,
        "assessments_taken": assessments_taken,
        "average_score": average_score if average_score is not None else "N/A",
        "completion_rate": f"{completion_rate:.2f}%" if assessments_taken else "N/A%",
        "top_scorers": list(top_scorers),
        "recent_activity_logs": list(recent_activity_logs),
    }

    return Response(data)

@api_view(['GET'])
def analytics_report(request):
    # Calculate average score
    avg_score = TestResult.objects.aggregate(Avg('score'))['score__avg'] or 0

    # Calculate highest score
    highest_score = TestResult.objects.aggregate(Max('score'))['score__max'] or 0

    # Count completed tests
    tests_completed = TestResult.objects.filter(completed=True).count()

    data = {
        "avg_score": f"{avg_score:.2f}%",  # Format as percentage
        "highest_score": highest_score,
        "tests_completed": tests_completed,
    }
    return Response(data)

@api_view(['GET'])
def user_management_overview(request):
    students_count = CustomUser.objects.filter(role='student').count()
    instructors_count =CustomUser.objects.filter(role='instructor', is_active=True).count()
    ongoing_tests_count = Test.objects.filter(is_ongoing=True).count()  # Updated name
    enrollments_count = Enrollment.objects.count()

    data = {
        "students_enrolled": students_count,
        "instructors_active": instructors_count,
        "ongoing_tests": ongoing_tests_count,
        "enrollment_open": enrollments_count,
    }
    return Response(data)

@api_view(['POST'])
def enroll_student(request):
    serializer = EnrollmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Student enrolled successfully!"}, status=201)
    return Response(serializer.errors, status=400)

# Manage Tests ViewSet
class ManageTestsViewSet(viewsets.ModelViewSet):
    queryset = ManageTests.objects.all()
    serializer_class = ManageTestsSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        return ManageTests.objects.filter(created_by=self.request.user)

# Question Views
class QuestionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

    def post(self, request):
        print("🛠 Incoming request data:", json.dumps(request.data, indent=2))  # Debugging

        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print("✅ Saved Question:", serializer.data)  # Debug output
            return Response(serializer.data, status=status.HTTP_201_CREATED)
       
        print("❌ Validation Errors:", serializer.errors)  # Debug errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuestionDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return None

    def get(self, request, pk):
        question = self.get_object(pk)
        if question is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = QuestionSerializer(question)
        return Response(serializer.data)

    def put(self, request, pk):
        question = self.get_object(pk)
        if question is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        print("🛠 Incoming request data:", json.dumps(request.data, indent=2))  # Debugging
        serializer = QuestionSerializer(question, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        question = self.get_object(pk)
        if question is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# User Response Views
class UserResponseListCreateView(generics.ListCreateAPIView):
    queryset = UserResponse.objects.all()
    serializer_class = UserResponseSerializer
    permission_classes = [IsAuthenticated]

class UserResponseDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserResponse.objects.all()
    serializer_class = UserResponseSerializer
    permission_classes = [IsAuthenticated]
from django.utils.timezone import now
@api_view(['GET'])
def dashboard_overview(request):
    total_tests = Test.objects.count()
    upcoming_tests = Test.objects.filter(scheduled_date__gt=now()).count()

    # Example performance calculation: average marks scored
    all_tests = Test.objects.all()
    total_marks = sum(test.total_marks for test in all_tests)
    max_score = sum(test.max_score for test in all_tests)
    overall_performance = (max_score / total_marks * 100) if total_marks else 0

    data = {
        'total_tests': total_tests,
        'upcoming_tests': upcoming_tests,
        'overall_performance': round(overall_performance, 2)
    }
    return Response(data)
class UserProfileView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
       
        # Get or create the UserProfile
        user_profile, created = UserProfile.objects.get_or_create(user=user)
       
        serializer = UserProfileSerializer(user_profile)
        response_data = serializer.data
       
        # Optionally, let the client know if the profile was created
        if created:
            response_data['message'] = "User profile was created as it didn't exist."

        return Response(response_data, status=status.HTTP_200_OK)
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
class CompletedTestCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CompletedTestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Test record saved successfully", "data": serializer.data}, status=201)
        return Response(serializer.errors, status=400)

# ✅ Performance Stats API
class PerformanceStatListCreateView(generics.ListCreateAPIView):
    serializer_class = PerformanceStatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PerformanceStat.objects.filter(user=self.request.user).order_by('-id')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# ✅ Recent Activities API
class RecentActivityListCreateView(generics.ListCreateAPIView):
    serializer_class = RecentActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RecentActivity.objects.filter(user=self.request.user).order_by('-timestamp')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
# Admin Settings ViewSet
class AdminSettingsViewSet(viewsets.ModelViewSet):
    serializer_class = AdminSettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AdminSettings.objects.filter(user=self.request.user)

# Performer Views
class PerformerListCreateView(generics.ListCreateAPIView):
    queryset = Performer.objects.all()
    serializer_class = PerformerSerializer
    permission_classes = [AllowAny]

class PerformerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Performer.objects.all()
    serializer_class = PerformerSerializer

# Feature Views
class FeatureListCreateView(generics.ListCreateAPIView):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer
    permission_classes = [AllowAny]
    
class ReviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            test = Test.objects.get(pk=pk, owner=request.user)  # Use 'owner' instead of 'user'
            reviews = test.reviews.all()
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Test.DoesNotExist:
            return Response({'error': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)
       
class ExportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            test = Test.objects.get(pk=pk, owner=request.user)

            buffer = io.BytesIO()
            p = canvas.Canvas(buffer)
            p.drawString(100, 750, "Certificate of Completion")
            p.drawString(100, 730, f"Test: {test.title}")
            p.drawString(100, 710, f"Score: {test.max_score}/{test.max_score}")
            p.drawString(100, 690, f"Date: {test.date.strftime('%Y-%m-%d')}")
            p.showPage()
            p.save()
            buffer.seek(0)
            return FileResponse(buffer, as_attachment=True, filename='certificate.pdf')
        except Test.DoesNotExist:
            return Response({'error': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)

class UserTestStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Fetch all attempted tests by the user
        attempted_tests = Test.objects.filter(owner=request.user, status='completed')

        # Total tests attempted
        total_attempted = attempted_tests.count()

        # Highest score
        highest_score = attempted_tests.aggregate(Max('max_score'))['max_score__max'] or 0

        # Accuracy calculation
        total_questions = sum(test.total_questions for test in attempted_tests)
        total_correct = sum(test.correct_answers for test in attempted_tests)
        accuracy = round((total_correct / total_questions) * 100, 2) if total_questions else 0

        # Certificates earned (e.g., tests with score >= 80%)
        certificates_earned = attempted_tests.filter(max_score__gte=80).count()

        stats_data = {
            "total_attempted": total_attempted,
            "highest_score": highest_score,
            "accuracy": accuracy,
            "certificates_earned": certificates_earned
        }

        return Response(stats_data, status=status.HTTP_200_OK)
   
class FeatureRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer

# Testimonial Views
class TestimonialListCreateView(generics.ListCreateAPIView):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    permission_classes = [AllowAny]

class TestimonialRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer

# FAQ Views
class FAQListCreateView(generics.ListCreateAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]

class FAQRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer

# Password Reset Views
class PasswordResetView(generics.CreateAPIView):
    queryset = PasswordReset.objects.all()
    serializer_class = PasswordResetSerializer
    permission_classes = [AllowAny]
   
class PerformanceHistoryView(APIView):
    def get(self, request):
        performance_history = PerformanceHistory.objects.all()
        serializer = PerformanceHistorySerializer(performance_history, many=True)
        return Response(serializer.data)
    def post(self, request):
        serializer = PerformanceHistorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the data to the database
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Contact Submission Views
class ContactMessageView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            # Create an admin notification
            AdminNotification.objects.create(message=f"New message from {serializer.validated_data['name']}")

            return Response({"message": "Message submitted successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminNotificationViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        notifications = AdminNotification.objects.all().order_by("-timestamp")
        serializer = AdminNotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def mark_as_read(self, request):
        AdminNotification.objects.all().update(read=True)
        return Response({"message": "Notifications marked as read"})
class QuestionCreateAPIView(APIView):
    def post(self, request):
        serializer = BulkQuestionSerializer(data=request.data)
        if serializer.is_valid():
            questions_data = serializer.validated_data['questions']
            question_objects = [Question(**q) for q in questions_data]
            Question.objects.bulk_create(question_objects)
            return Response({"message": "Questions created successfully"}, status=status.HTTP_201_CREATED)
       
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
from django.utils import timezone  # Add this import

class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all().order_by('-created_at')
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        title = serializer.validated_data['title']
        message = serializer.validated_data['message']

        # Check for duplicates
        if Announcement.objects.filter(title=title, message=message).exists():
            return Response({"detail": "Duplicate announcement exists."}, status=400)

        # Set today's date if not provided
        if 'date' not in serializer.validated_data:
            serializer.validated_data['date'] = timezone.now().date()

        # Save normally
        serializer.save(created_by=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.select_related('announcement')  # Prefetch related data
    serializer_class = NotificationSerializer
@api_view(["POST"])
def mark_notifications_as_read(request):
        notifications = Notification.objects.filter(user=request.user)

        return Response({"message": "Notifications marked as read"})
class AnnouncementDetailView(generics.RetrieveDestroyAPIView):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]

class TestListView(generics.ListAPIView):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    permission_classes = [IsAuthenticated]

class AttemptedTestViewSet(viewsets.ModelViewSet):
    queryset = AttemptedTest.objects.all()
    serializer_class = AttemptedTestSerializer

    @action(detail=False, methods=["post"])
    def submit_attempt(self, request):
        user_id = request.data.get("user")
        attempted_tests = request.data.get("attempted_tests", [])

        if not user_id or not attempted_tests:
            return Response({"error": "User and attempted_tests fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        saved_attempts = []
        errors = []

        for test_data in attempted_tests:
            test_id = test_data.get("test")

            try:
                test = Test.objects.get(id=test_id)
            except Test.DoesNotExist:
                errors.append({"error": f"Test with id {test_id} not found."})
                continue

            test_data["user"] = user.id  # Assign user ID
            test_data["test"] = test.id  # Assign test ID

            serializer = AttemptedTestSerializer(data=test_data)
            if serializer.is_valid():
                saved_attempt = serializer.save()
                saved_attempts.append(serializer.data)
            else:
                errors.append(serializer.errors)

        if errors:
            return Response({"saved_attempts": saved_attempts, "errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response(saved_attempts, status=status.HTTP_201_CREATED)
class AchievementView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        achievements = Achievement.objects.all()
        serializer = AchievementSerializer(achievements, many=True)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_questions(request):
    source_test_id = request.data.get('source_test_id')
    target_test_id = request.data.get('target_test_id')

    if not source_test_id or not target_test_id:
        return Response({"error": "source_test_id and target_test_id are required."}, status=400)

    try:
        source_test = Test.objects.get(id=source_test_id)  # Removed is_public=True
        target_test = Test.objects.get(id=target_test_id)
    except Test.DoesNotExist:
        return Response({"error": "Invalid test IDs"}, status=400)

    questions = Question.objects.filter(test=source_test)
    for q in questions:
        Question.objects.create(
            test=target_test,
            text=q.text,
            type=q.type,
            options=json.loads(json.dumps(q.options)),  # Ensure deep copy
            correct_answer=json.loads(json.dumps(q.correct_answer))
        )

    target_test.total_questions = Question.objects.filter(test=target_test).count()
    target_test.save()

    return Response({"message": "Questions imported successfully!"}, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_questions_from_test(request, test_id):
    questions = Question.objects.filter(test_id=test_id)
    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def public_tests(request):
    tests = Test.objects.filter(is_public=True).exclude(owner=request.user)
    serializer = TestSerializer(tests, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_test_user(request):
    data = request.data

    name = data.get('name')
    email = data.get('email')
    test_id = data.get('test_id')

    if not test_id or not email:
        return Response({"error": "test_id and email required."}, status=400)

    normalized_email = email.strip().lower()

    try:
        test = Test.objects.get(id=test_id)
    except Test.DoesNotExist:
        return Response({"error": "Test not found."}, status=404)

    # ✅ Save participant info
    TestParticipant.objects.get_or_create(
        test=test,
        email=normalized_email,
        defaults={"name": name or "Unknown"}
    )

    # ✅ New logic to allow unprotected tests
    if test.access_type == "unprotected":
        return Response({"message": "Access granted."}, status=200)

    # ✅ Protected logic
    if not AllowedParticipant.objects.filter(test=test, email=normalized_email).exists():
        return Response({"error": "You are not allowed to take this test."}, status=403)

    return Response({"message": "Access granted."}, status=200)


@api_view(['GET'])
def get_leaderboard(request):
    leaderboard = LeaderboardEntry.objects.all().order_by('rank')
    sort_by = request.GET.get('sort', 'rank')
    if sort_by == "score":
        leaderboard = leaderboard.order_by('-score')
        serializer = LeaderboardEntrySerializer(leaderboard, many=True)
        return Response(serializer.data)
class AchievementRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [IsAuthenticated]

# Test Summary Views
class TestSummaryList(generics.ListAPIView):
    queryset = TestSummary.objects.all()
    serializer_class = TestSummarySerializer
    permission_classes = [IsAuthenticated]

class TestSummaryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = TestSummary.objects.all()
    serializer_class = TestSummarySerializer
    permission_classes = [IsAuthenticated]
class AvailableTestsView(generics.ListAPIView):
    serializer_class = TestSubmissionSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        return user.available_tests.all()
class UserResponseListCreateView(generics.ListCreateAPIView):
    queryset = UserResponse.objects.all()
    serializer_class = UserResponseSerializer

def normalize(value):
    if isinstance(value, list):
        return sorted([str(v).strip().lower() for v in value])
    elif isinstance(value, str):
        return [value.strip().lower()]
    elif value is None:
        return []
    return [str(value).strip().lower()]

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_test(request):
    """
    Handles test submission, calculates score, and updates user test history.
    """
    user = request.user
    test_id = request.data.get('test_id')
    answers = request.data.get('answers', [])  # List of answers [{question_id: 1, selected_option: [...]}, ...]

    try:
        test = Test.objects.get(id=test_id)
    except Test.DoesNotExist:
        return Response({"error": "Invalid test ID"}, status=400)

    if TestAttempt.objects.filter(user=user, test=test, status="ongoing").exists():
        return Response({"error": "You have an ongoing attempt for this test."}, status=400)

    attempt = TestAttempt.objects.create(user=user, test=test, status="completed", end_time=now())

    correct_answers = 0
    total_questions = test.questions.count()

    for answer in answers:
        question_id = answer.get("question_id")
        selected_option = answer.get("selected_option")

        try:
            question = Question.objects.get(id=question_id, test=test)
        except Question.DoesNotExist:
            continue

        UserAnswer.objects.create(attempt=attempt, question=question, selected_option=selected_option)

        if sorted(selected_option) == sorted(question.correct_answer):
            correct_answers += 1

    # Calculate score
    score = correct_answers * (test.marks_per_question or 1)
    attempt.score = score
    attempt.status = "completed"
    attempt.save()

    return Response({
        "message": "Test submitted successfully",
        "attempt_id": attempt.id,
        "score": score,
        "total_questions": total_questions
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_test_stats(request):
    """
    Retrieves user test statistics for the dashboard.
    """
    user = request.user
    total_attempted = TestAttempt.objects.filter(user=user).count()
    highest_score = TestAttempt.objects.filter(user=user).aggregate(Max('score'))['score__max'] or 0
    accuracy = (TestAttempt.objects.filter(user=user, score__gt=0).count() / total_attempted) * 100 if total_attempted > 0 else 0
    certificates_earned = TestAttempt.objects.filter(user=user, score__gte=50).count()  # Assuming 50+ score earns a certificate

    return Response({
        "total_attempted": total_attempted,
        "highest_score": highest_score,
        "accuracy": round(accuracy, 2),
        "certificates_earned": certificates_earned
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_attempted_tests(request):
    """
    Retrieves a list of attempted tests for the user.
    """
    attempts = TestAttempt.objects.filter(user=request.user).order_by('-end_time')
    serializer = TestAttemptSerializer(attempts, many=True)
    return Response(serializer.data)
from django.db.models import Avg, Count, F
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def leaderboard(request):
    """
    Retrieves leaderboard with all test attempts by each user.
    """

    if request.method == 'POST':
        # Handle score submission
        user_id = request.data.get('user_id')
        score = request.data.get('score')
        test_id = request.data.get('testId')
        total_questions = request.data.get('total_questions', 0)  # Get total questions, default to 0

        # Save the score to the TestAttempt model
        TestAttempt.objects.create(
            user_id=user_id,
            score=score,
            test_id=test_id,
            total_questions=total_questions  # Ensure this is saved
        )


        # ✅ Ensure `test_id` is valid
        try:
            test = get_object_or_404(Test, id=int(test_id))
        except (ValueError, Test.DoesNotExist):
            return Response({"error": "Invalid test ID"}, status=400)

        # ✅ Save the test attempt
        TestAttempt.objects.create(user_id=user_id, score=score, test=test, total_questions=total_questions)

    # Retrieve all tests attempted by users in the leaderboard
    user_attempts = TestAttempt.objects.values(
        username=F('user__username'),
        test_title=F('test__title'),
        attempted_test_id=F('test__id'),
        attempt_date=F('timestamp')
    ).annotate(
        total_score=F('score'),
        total_questions=F('total_questions')
    ).order_by('-total_score')

    # Assign badges based on score & total questions
    for attempt in user_attempts:
        attempt['badges'] = assign_badges(attempt['total_score'], attempt['total_questions'])

    return Response(user_attempts) if user_attempts else Response({"message": "No leaderboard data available"}, status=404)

def assign_badges(score, total_questions):
    badges = []
   
    # ✅ Ensure score and total_questions are not None
    score = score if score is not None else 0
    total_questions = total_questions if total_questions is not None else 0

    if score >= 90 and total_questions >= 10:
        badges.append("Gold Badge")
    elif score >= 75 and total_questions >= 5:
        badges.append("Silver Badge")
    elif score >= 50:
        badges.append("Bronze Badge")  
       
    return badges
@api_view(['POST'])
def upload_allowed_emails(request):
    test_id = request.data.get('test_id')
    raw_emails = request.data.get('emails')  # This should now be a **comma-separated string**

    if not test_id or not raw_emails:
        return Response({"error": "test_id and emails required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        test = Test.objects.get(id=test_id)
    except Test.DoesNotExist:
        return Response({"error": "Test not found."}, status=status.HTTP_404_NOT_FOUND)

    # ✅ Parse comma-separated emails
    emails = [email.strip().lower() for email in raw_emails.split(',') if email.strip()]

    # ❌ Empty after split?
    if not emails:
        return Response({"error": "No valid emails provided."}, status=status.HTTP_400_BAD_REQUEST)

    # 🔄 Clear old participants for the test
    AllowedParticipant.objects.filter(test=test).delete()

    # ✅ Save new participants
    allowed_objs = [AllowedParticipant(test=test, email=email) for email in emails]
    AllowedParticipant.objects.bulk_create(allowed_objs)

    # 🔐 Generate secure link
    from .utils import encode_testid_to_secure_uuid
    secure_uuid = encode_testid_to_secure_uuid(test.id)

    BASE_URL = "http://localhost:3000/"
    test_link = f"{BASE_URL}smartbridge/online-test-assessment/{secure_uuid}"

    # 📧 Send invitations
    send_test_invite_emails(emails, test_link)

    return Response({"message": f"{len(allowed_objs)} emails saved and invitations sent."}, status=status.HTTP_201_CREATED)

def send_test_invite_emails(emails, test_link):
    subject = "Your Access Link for the Online Test"
    message = f"""
                Hello,

                You have been invited to take an online test.

                Click the link below to start:
                {test_link}

                Good luck!
                """
    from_email = settings.DEFAULT_FROM_EMAIL

    for email in emails:
        try:
            send_mail(subject, message, from_email, [email], fail_silently=False)
            print(f"✅ Invitation sent to {email}")
        except Exception as e:
            print(f"❌ Failed to send email to {email}: {e}")

@api_view(['GET'])
@permission_classes([AllowAny])
def decode_uuid_and_get_test_id(request, uuid_str):
    try:
        test_id = decode_secure_uuid_to_testid(uuid_str)  # this uses your XOR function
        return Response({"test_id": test_id}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": "Invalid UUID"}, status=status.HTTP_400_BAD_REQUEST)
class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer

    def get_serializer_context(self):
        return {**super().get_serializer_context(), "request": self.request}

    def create(self, request):
        """Create a new test"""
        print("Raw Request Data:", request.data)
        data = request.data
        questions = data.get("questions", [])
        for q in questions:
            print("Received Question:", q)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.shortcuts import get_object_or_404

@method_decorator(csrf_exempt, name='dispatch')
class TestAttemptViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        """Start a new test attempt"""
        user = request.user
        test_id = request.data.get("test_id")
        raw_email = request.data.get("email")
        test = get_object_or_404(Test, id=test_id)
        start_time = timezone.now()  # ✅ correct assignment

        normalized_email = raw_email.strip().lower() if raw_email else None

        # Get or create participant
        participant = None
        if normalized_email:
            participant = TestParticipant.objects.filter(test=test, email=normalized_email).first()
            if not participant:
                participant = TestParticipant.objects.create(
                    test=test,
                    email=normalized_email,
                    name=user.username or "Anonymous"
                )

        # ✅ Now use start_time when creating the attempt
        attempt = TestAttempt.objects.create(
            user=user,
            test=test,
            email=normalized_email,
            start_time=start_time
        )

        return Response(TestAttemptSerializer(attempt).data, status=status.HTTP_201_CREATED)


    def retrieve(self, request, pk=None):
        """Retrieve a single test attempt"""
        attempt = get_object_or_404(TestAttempt, id=pk, user=request.user)
        serializer = TestAttemptSerializer(attempt)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def normalize(value):
        if isinstance(value, list):
            return sorted([str(v).strip().lower() for v in value])
        elif isinstance(value, str):
            return [value.strip().lower()]
        elif value is None:
            return []
        return [str(value).strip().lower()]

    def update(self, request, pk=None):
        """Update test attempt — records answers, computes percentage score, and finalizes attempt"""
        attempt = get_object_or_404(TestAttempt, id=pk, user=request.user)

        if attempt.status == "completed":
            return Response({"error": "This test attempt is already completed."}, status=status.HTTP_400_BAD_REQUEST)

        answers_data = request.data.get("answers", [])

        correct_answers = 0
        total_questions = 0

        # Save each answer
        for answer_data in answers_data:
            question_id = answer_data.get("question")
            selected_option = answer_data.get("selected_option")

            if not question_id or selected_option is None:
                continue

            question = get_object_or_404(Question, id=question_id)

            # Avoid duplicate answers
            if UserAnswer.objects.filter(attempt=attempt, question=question).exists():
                continue

            UserAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_option=selected_option
            )

            if question.correct_answer is not None and str(question.correct_answer).strip() != "":
                total_questions += 1
                if normalize(selected_option) == normalize(question.correct_answer):
                    correct_answers += 1

        # Calculate percentage score
        if total_questions > 0:
            score_percentage = round((correct_answers / total_questions) * 100, 2)
        else:
            score_percentage = 0.0

        # Update TestAttempt
        attempt.total_questions = total_questions
        attempt.correct_answers = correct_answers
        attempt.score = score_percentage
        attempt.end_time = now()
        attempt.passed = score_percentage >= (attempt.test.pass_criteria or 50)
        attempt.status = "completed" if total_questions > 0 else "ongoing"
        attempt.save()

        # Email notification
        test = attempt.test
        if test.receive_email_notifications and test.notification_emails:
            recipients = [email.strip() for email in test.notification_emails.split(",") if email.strip()]
            send_mail(
                subject=f"[Test Completed] {test.title}",
                message=f"User {request.user.username} ({request.user.email}) has completed the test '{test.title}' with a score of {attempt.score:.2f}%",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,
            )
            send_congratulations_email(request.user, attempt, test)

        return Response(TestAttemptSerializer(attempt).data, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        """
        When a test attempt is updated, check if it's completed and save it.
        """
        instance = serializer.save()

        if instance.status == "completed" and instance.score is not None:
            save_completed_test(instance.user, instance)

    def list(self, request):
        """Fetch all attempted tests of the user"""
        user = request.user
        attempts = TestAttempt.objects.filter(user=user).order_by('-end_time')
        serializer = TestAttemptSerializer(attempts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_user_statistics(self, request):
        """Retrieve user statistics: highest score, accuracy, certificates earned"""
        user = request.user
        attempts = TestAttempt.objects.filter(user=user)
        highest_score = attempts.aggregate(Max('score'))['score__max'] or 0
        total_correct = attempts.aggregate(Sum('correct_answers'))['correct_answers__sum'] or 0
        total_questions = attempts.aggregate(Sum('total_questions'))['total_questions__sum'] or 1
        accuracy = round((total_correct / total_questions) * 100, 2) if total_questions > 0 else 0
        certificates_earned = attempts.filter(score__gte=50).count()

        return Response({
            "highest_score": highest_score,
            "accuracy": accuracy,
            "certificates_earned": certificates_earned
        }, status=status.HTTP_200_OK)

    def get_user_rank(self, request, test_id):
        """Calculate user rank based on test scores"""
        user = request.user
        all_attempts = TestAttempt.objects.filter(test_id=test_id).order_by('-score')

        rank = None
        for index, attempt in enumerate(all_attempts, start=1):
            if attempt.user == user:
                rank = index
                break

        return Response({"rank": rank}, status=status.HTTP_200_OK)

    def get_object(self, pk):
        return get_object_or_404(TestAttempt, pk=pk)

    @action(detail=True, methods=["get"])
    def review(self, request, pk=None):
        """Review test attempt answers"""
        test_attempt = self.get_object(pk)
        answers = UserAnswer.objects.filter(attempt=test_attempt)

        review_data = ReviewSerializer(test_attempt)
        return Response(review_data.data, status=200)

class AchievementsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        completed_tests = CompletedTest.objects.filter(user=user)

        achievements = self.calculate_achievements(completed_tests)

        return Response({"achievements": achievements}, status=status.HTTP_200_OK)

    def calculate_achievements(self, completed_tests):
        achievements = []

        # Achievement 1: Completed 10 Tests
        if completed_tests.count() >= 10:
            achievements.append("Completed 10 Tests")

        # Achievement 2: High Scorer
        high_scorer_count = completed_tests.filter(score__gte=90).count()
        if high_scorer_count >= 5:
            achievements.append("High Scorer")

        # Achievement 3: Perfect Score
        perfect_score_count = completed_tests.filter(score=100).count()
        if perfect_score_count > 0:
            achievements.append("Perfect Score")

        # Achievement 4: Subject Mastery
        subject_counts = completed_tests.values('subject').annotate(count=models.Count('subject'))
        for subject in subject_counts:
            if subject['count'] >= 5:
                achievements.append(f"Master of {subject['subject']}")

        # Achievement 5: Consistent Performer
        if completed_tests.exists():
            average_score = completed_tests.aggregate(models.Avg('score'))['score__avg']
            if average_score and average_score >= 85:
                achievements.append("Consistent Performer")

        # Achievement 6: Diverse Subjects
        unique_subjects = completed_tests.values_list('subject', flat=True).distinct()
        if unique_subjects.count() >= 3:
            achievements.append("Diverse Learner")

        return achievements  
from django.utils import timezone
@api_view(['GET'])
def test_report(request, test_id):
    try:
        attempt = TestAttempt.objects.get(id=test_id, user=request.user)
        serializer = TestAttemptSerializer(attempt)
        return Response(serializer.data)
    except TestAttempt.DoesNotExist:
        return Response({"error": "Test not found"}, status=404)
def complete_test(user, test_attempt):
    # Mark the test attempt as completed
    test_attempt.is_completed = True
    test_attempt.completed_at = timezone.now()  # Set the completion time
    test_attempt.save()  # Save the changes to the database

    # Create a notification for the user
    user_message = f"You have completed the test: {test_attempt.test.title}."
    Notification.objects.create(user=user, message=user_message)

    # Create a notification for the admin
    admin_message = f"User  {user.username} has completed the test: {test_attempt.test.title}."
   
    # Fetch all admin users (assuming they are marked as staff)
    admin_users = CustomUser.objects.filter(is_staff=True)  # Adjust this query based on your admin user setup
    for admin in admin_users:
        Notification.objects.create(user=admin, admin=True, message=admin_message)
def complete_test_view(request, test_attempt_id):
    # Fetch the test attempt object
    test_attempt = get_object_or_404(TestAttempt, id=test_attempt_id)

    # Ensure the user is allowed to complete the test
    if request.user == test_attempt.user:
        complete_test(request.user, test_attempt)  # Call the function to complete the test
        return JsonResponse({"message": "Test completed successfully."}, status=200)
    else:
        return JsonResponse({"error": "You are not authorized to complete this test."}, status=403)
def fetch_admin_notifications(request):
    if request.user.is_authenticated and request.user.is_staff:
        notifications = Notification.objects.filter(admin=True).order_by('-created_at')
        notification_list = list(notifications.values('id', 'message', 'created_at', 'is_read'))
        return JsonResponse(notification_list, safe=False)
    return JsonResponse([], safe=False)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_consent(request, test_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            microphone = data.get("microphone", False)
            location = data.get("location", False)
            network = data.get("network", False)
            phone = data.get("phone", False)
            test_attempt = TestAttempt.objects.filter(user=request.user, test_id=test_id).latest('id')

            # Save the consent data (or update existing attempt)
            test_attempt, created = TestAttempt.objects.get_or_create(
                user=request.user,
                test_id=test_id,
                defaults={"microphone": microphone, "location": location, "network": network, "phone": phone},
            )

            if not created:
                # Update existing consent values
                test_attempt.microphone = microphone
                test_attempt.location = location
                test_attempt.network = network
                test_attempt.phone = phone
                test_attempt.save()

            return JsonResponse({"message": "Consent saved successfully"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
 
    permission_classes = [AllowAny]

class UserAnswerViewSet(viewsets.ModelViewSet):
    queryset = UserAnswer.objects.all()
    serializer_class = UserAnswerSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        """Save user answers"""
        data = request.data
        attempt = TestAttempt.objects.get(id=data.get("attempt"))

        for answer in data.get("answers", []):
            question = Question.objects.get(id=answer["question"])
            UserAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_option=answer["selected_option"]
            )

        return Response({"message": "Answers saved successfully"}, status=status.HTTP_201_CREATED)
   
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .models import Test, Question
import csv, io, json, re
from PyPDF2 import PdfReader # type: ignore

class UploadQuestionsView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        file = request.FILES.get('file')
        test_id = request.data.get('test_id')

        if not file or not test_id:
            return Response({'error': 'File and test_id are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            return Response({'error': 'Test not found.'}, status=status.HTTP_404_NOT_FOUND)

        questions_created = 0

        if file.name.endswith('.csv'):
            decoded_file = file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)

            for row in reader:
                try:
                    Question.objects.create(
                        test=test,
                        text=row['text'],
                        type=row['type'],
                        options=json.loads(row.get('options', '[]')),
                        correct_answer=json.loads(row.get('correct_answer', '[]')),
                    )
                    questions_created += 1
                except Exception as e:
                    return Response({'error': f"Failed to process row: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        elif file.name.endswith('.pdf'):
            pdf_reader = PdfReader(file)
            lines = []
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    lines.extend(page_text.strip().split('\n'))

            questions = []
            current_block = []

            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if re.match(r'^[A-Z].*\?$', line) or '____' in line or '__________' in line:
                    if current_block:
                        questions.append(current_block)
                    current_block = [line]
                else:
                    current_block.append(line)

            if current_block:
                questions.append(current_block)

            for block in questions:
                question_text = block[0]
                options = []
                correct_answer = []
                answer_line = None

                for line in block[1:]:
                    if line.lower().startswith('answer:'):
                        answer_line = line
                        continue
                    match = re.match(r'^(\d+)\.\s*(.+)', line.strip())
                    if match:
                        options.append(match.group(2).strip())

                if '____' in question_text or '__________' in question_text:
                    q_type = 'fillintheblank'
                    if answer_line:
                        correct_answer = [answer_line.split(':', 1)[1].strip()]
                elif len(options) == 2 and set(opt.lower() for opt in options) == {"true", "false"}:
                    q_type = 'truefalse'
                    if answer_line:
                        correct_answer = [answer_line.split(':', 1)[1].strip().capitalize()]
                elif answer_line and ',' in answer_line:
                    q_type = 'multipleresponse'
                    indices = [int(i.strip()) - 1 for i in answer_line.split(':', 1)[1].split(',')]
                    correct_answer = [options[i] for i in indices if 0 <= i < len(options)]
                elif options:
                    q_type = 'multiplechoice'
                    if answer_line:
                        idx = int(answer_line.split(':', 1)[1].strip()) - 1
                        if 0 <= idx < len(options):
                            correct_answer = [options[idx]]
                else:
                    q_type = 'fillintheblank'
                    if answer_line:
                        correct_answer = [answer_line.split(':', 1)[1].strip()]

                Question.objects.create(
                    test=test,
                    text=question_text,
                    type=q_type,
                    options=options,
                    correct_answer=correct_answer
                )
                questions_created += 1

        else:
            return Response({'error': 'Unsupported file type. Only .csv and .pdf allowed.'}, status=status.HTTP_400_BAD_REQUEST)

        if questions_created == 0:
            return Response({'error': 'No valid questions were imported.'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Update totals only once, after all questions added
        test.update_totals()

        return Response({'message': f'{questions_created} questions imported successfully'}, status=status.HTTP_201_CREATED)



from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
import csv, json, io, re
from PyPDF2 import PdfReader

class ParseUploadedQuestionsView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        file = request.FILES.get('file')

        if not file:
            return Response({'error': 'File is required.'}, status=status.HTTP_400_BAD_REQUEST)

        questions = []

        if file.name.endswith('.csv'):
            try:
                decoded_file = file.read().decode('utf-8')
                io_string = io.StringIO(decoded_file)
                reader = csv.DictReader(io_string)

                for row in reader:
                    question = {
                        'text': row.get('text', '').strip(),
                        'type': row.get('type', '').strip(),
                        'options': json.loads(row.get('options', '[]')),
                        'correct_answer': json.loads(row.get('correct_answer', '[]'))
                    }
                    questions.append(question)
            except Exception as e:
                return Response({'error': f'CSV parse error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        elif file.name.endswith('.pdf'):
            try:
                pdf_reader = PdfReader(file)
                lines = []
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        lines.extend(page_text.strip().split('\n'))

                current_block = []
                raw_questions = []

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    if re.match(r'^[A-Z].*\?$', line) or '____' in line or '__________' in line:
                        if current_block:
                            raw_questions.append(current_block)
                        current_block = [line]
                    else:
                        current_block.append(line)

                if current_block:
                    raw_questions.append(current_block)

                for block in raw_questions:
                    question_text = block[0]
                    options = []
                    correct_answer = []
                    answer_line = None

                    for line in block[1:]:
                        if line.lower().startswith('answer:'):
                            answer_line = line
                            continue
                        match = re.match(r'^(\d+)\.\s*(.+)', line.strip())
                        if match:
                            options.append(match.group(2).strip())

                    if '____' in question_text or '__________' in question_text:
                        q_type = 'fillintheblank'
                        if answer_line:
                            correct_answer = [answer_line.split(':', 1)[1].strip()]
                    elif len(options) == 2 and set(opt.lower() for opt in options) == {"true", "false"}:
                        q_type = 'truefalse'
                        if answer_line:
                            correct_answer = [answer_line.split(':', 1)[1].strip().capitalize()]
                    elif answer_line and ',' in answer_line:
                        q_type = 'multipleresponse'
                        indices = [int(i.strip()) - 1 for i in answer_line.split(':', 1)[1].split(',')]
                        correct_answer = [options[i] for i in indices if 0 <= i < len(options)]
                    elif options:
                        q_type = 'multiplechoice'
                        if answer_line:
                            idx = int(answer_line.split(':', 1)[1].strip()) - 1
                            if 0 <= idx < len(options):
                                correct_answer = [options[idx]]
                    else:
                        q_type = 'fillintheblank'
                        if answer_line:
                            correct_answer = [answer_line.split(':', 1)[1].strip()]

                    questions.append({
                        'text': question_text,
                        'type': q_type,
                        'options': options,
                        'correct_answer': correct_answer
                    })

            except Exception as e:
                return Response({'error': f'PDF parse error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'error': 'Unsupported file type. Only .csv and .pdf allowed.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'questions': questions}, status=status.HTTP_200_OK)

class CaptureImageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if 'image' not in request.FILES:
            return Response(
                {'success': False, 'message': 'No image provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            image_file = request.FILES['image']
            user = request.user

            # Create user-specific directory
            user_dir = os.path.join(settings.MEDIA_ROOT, 'captures', str(user.id))
            os.makedirs(user_dir, exist_ok=True)

            # Read image content into memory once
            image_bytes = image_file.read()

            # Save image permanently
            filename = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            file_path = os.path.join(user_dir, filename)
            default_storage.save(file_path, ContentFile(image_bytes))

            # Write image to temporary file for OpenCV
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                tmp.write(image_bytes)
                tmp_path = tmp.name

            try:
                # Load image using OpenCV
                img = cv2.imread(tmp_path)
                if img is None:
                    raise ValueError("Could not read the image file")

                # Convert to grayscale
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                # Load OpenCV face detector
                face_cascade = cv2.CascadeClassifier(
                    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                )

                # Detect faces
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(100, 100)
                )

                # Validation logic
                validation = {
                    'face_detected': len(faces) > 0,
                    'multiple_faces': len(faces) > 1,
                    'looking_straight': False,
                    'is_valid': False,
                    'message': ''
                }

                if not validation['face_detected']:
                    validation['message'] = 'No face detected'
                elif validation['multiple_faces']:
                    validation['message'] = 'Multiple faces detected'
                else:
                    # Check if face is centered
                    (x, y, w, h) = faces[0]
                    face_center_x = x + w / 2
                    img_center_x = img.shape[1] / 2

                    if abs(face_center_x - img_center_x) < img.shape[1] * 0.1:
                        validation['looking_straight'] = True
                        validation['is_valid'] = True
                        validation['message'] = 'Valid capture'
                    else:
                        validation['message'] = 'Face not centered'

                return Response({
                    'success': validation['is_valid'],
                    'message': validation['message'],
                    'validation': validation,
                    'image_url': default_storage.url(file_path),
                    'user': {
                        'id': user.id,
                        'username': user.username
                    }
                })

            finally:
                # Delete temp file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

        except Exception as e:
            return Response(
                {'success': False, 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )