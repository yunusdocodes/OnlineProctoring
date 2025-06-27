from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, permissions

from .models import (
    Category, Performer, Feature, Testimonial, Test,
    TestAttempt, FAQ, TestSettings, AdminSettings, TestSummary, CompletedTest, UserResponse
)
from .serializers import (
    UserProfileSerializer, CategorySerializer, PerformerSerializer,
    FeatureSerializer, TestimonialSerializer, TestSerializer,
    TestAttemptSerializer, FAQSerializer, TestSettingsSerializer,
    LoginSerializer, AdminSettingsSerializer, ChangePasswordSerializer, TestSummarySerializer, CompletedTestSerializer, UserResponseSerializer
)

User  = get_user_model()

class UserDataView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        if not user.check_password(old_password):
            return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'success': 'Password changed successfully'}, status=status.HTTP_200_OK)

class UploadProfilePictureView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = request.user
        avatar = request.FILES.get('avatar')
        if avatar:
            user.avatar = avatar
            user.save()
            return Response({'avatarUrl': user.avatar.url}, status=status.HTTP_200_OK)
        return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

class DeactivateAccountView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return Response({'success': 'Account deactivated successfully'}, status=status.HTTP_204_NO_CONTENT)

# Completed Tests View
class CompletedTestList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompletedTestSerializer

    def get_queryset(self):
        user_email = self.request.user.email  # Assuming you want to filter by the user's email
        return CompletedTest.objects.filter(user_email=user_email)

# Achievements View
class AchievementsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Replace with actual logic to fetch achievements for the user
        return []

# Performance Stats View
class PerformanceStatsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Replace with actual logic to fetch performance stats for the user
        return Response({'total_tests': 10, 'average_score': 75})

# Login View using JWT
class LoginView(generics.GenericAPIView):
    permission_classes = []  # No authentication needed for login
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(username=username, password=password)
            if user is None:
                return Response({"detail": "Invalid credentials. Please check your username and password."}, status=status.HTTP_401_UNAUTHORIZED)

            # Generate the JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Category views
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# Performer views
class PerformerListCreateView(generics.ListCreateAPIView):
    queryset = Performer.objects.all()
    serializer_class = PerformerSerializer

class PerformerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Performer.objects .all()
    serializer_class = PerformerSerializer

# Feature views
class FeatureListCreateView(generics.ListCreateAPIView):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer

class FeatureRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer

# Testimonial views
class TestimonialListCreateView(generics.ListCreateAPIView):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer

class TestimonialRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer

# Test views
class TestListCreateView(generics.ListCreateAPIView):
    queryset = Test.objects.all()
    serializer_class = TestSerializer

class TestRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Test.objects.all()
    serializer_class = TestSerializer

# TestAttempt views
class TestAttemptListCreateView(generics.ListCreateAPIView):
    queryset = TestAttempt.objects.all()
    serializer_class = TestAttemptSerializer

class TestAttemptRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TestAttempt.objects.all()
    serializer_class = TestAttemptSerializer

# FAQ views
class FAQListCreateView(generics.ListCreateAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer

class FAQRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer

# TestSettings views
class TestSettingsView(generics.RetrieveUpdateAPIView):
    queryset = TestSettings.objects.all()
    serializer_class = TestSettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return TestSettings.objects.get(test_id=self.kwargs['test_id'])
        except TestSettings.DoesNotExist:
            raise Response({"detail": "TestSettings not found for this test."}, status=status.HTTP_404_NOT_FOUND)

# AdminSettings views
class AdminSettingsViewSet(viewsets.ModelViewSet):
    queryset = AdminSettings.objects.all()
    serializer_class = AdminSettingsSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Test Summary Views
class TestSummaryList(generics.ListAPIView):
    queryset = TestSummary.objects.all()
    serializer_class = TestSummarySerializer
    permission_classes = [permissions.IsAuthenticated]  # Ensure only authenticated users can access

class TestSummaryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = TestSummary.objects.all()
    serializer_class = TestSummarySerializer
    permission_classes = [permissions.IsAuthenticated]  # Ensure only authenticated users can access

# Completed Test Views
class CompletedTestsView(generics.ListAPIView):
    serializer_class = CompletedTestSerializer
    permission_classes = [permissions.IsAuthenticated]  # Ensure only authenticated users can access

    def get_queryset(self):
        # Return all completed tests for the authenticated user
        user = self.request.user
        return CompletedTest.objects.filter(user=user)  # Filter by the logged-in user

class CompletedTestList(generics.ListAPIView):
    queryset = CompletedTest.objects.all()
    serializer_class = CompletedTestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        print(f"Fetching completed tests for user: {user.username} (ID: {user.id})")  # Debugging line
        queryset = super().get_queryset().filter(user=user)
        print(f"Number of completed tests found: {queryset.count()}")  # Debugging line
        return queryset

# User Response Views
class UserResponseListCreateView(generics.ListCreateAPIView):
    queryset = UserResponse.objects.all()
    serializer_class = UserResponseSerializer