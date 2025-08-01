# newapp/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserProfileListCreateView,
    UserProfileRetrieveUpdateDestroyView,
    CategoryListCreateView,
    CategoryRetrieveUpdateDestroyView,
    PerformerListCreateView,
    PerformerRetrieveUpdateDestroyView,
    FeatureListCreateView,
    FeatureRetrieveUpdateDestroyView,
    TestimonialListCreateView,
    TestimonialRetrieveUpdateDestroyView,
    TestListCreateView,
    TestRetrieveUpdateDestroyView,
    TestAttemptListCreateView,
    TestAttemptRetrieveUpdateDestroyView,
    FAQListCreateView,
    FAQRetrieveUpdateDestroyView,
    TestSettingsView,
    ChangePasswordView,
    DeactivateAccountView,
    LoginView,
    AdminSettingsViewSet  # Ensure this matches your view class name
)

# Create a router and register your viewsets with it
router = DefaultRouter()
router.register(r'admin-settings', AdminSettingsViewSet, basename='admin-settings')

urlpatterns = [
    # UserProfile URLs
    path('user-profile/', UserProfileListCreateView.as_view(), name='user-profile-list-create'),
    path('user-profile/<int:pk>/', UserProfileRetrieveUpdateDestroyView.as_view(), name='user-profile-retrieve-update-destroy'),

    # Category URLs
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryRetrieveUpdateDestroyView.as_view(), name='category-retrieve-update-destroy'),

    # Performer URLs
    path('performers/', PerformerListCreateView.as_view(), name='performer-list-create'),
    path('performers/<int:pk>/', PerformerRetrieveUpdateDestroyView.as_view(), name='performer-retrieve-update-destroy'),

    # Feature URLs
    path('features/', FeatureListCreateView.as_view(), name='feature-list-create'),
    path('features/<int:pk>/', FeatureRetrieveUpdateDestroyView.as_view(), name='feature-retrieve-update-destroy'),

    # Testimonial URLs
    path('testimonials/', TestimonialListCreateView.as_view(), name='testimonial-list-create'),
    path('testimonials/<int:pk>/', TestimonialRetrieveUpdateDestroyView.as_view(), name='testimonial-retrieve-update-destroy'),

    # Test URLs
    path('tests/', TestListCreateView.as_view(), name='test-list-create'),
    path('tests/<int:pk>/', TestRetrieveUpdateDestroyView.as_view(), name='test-retrieve-update-destroy'),

    # TestAttempt URLs
    path('test-attempts/', TestAttemptListCreateView.as_view(), name='test-attempt-list-create'),
    path('test-attempts/<int:pk>/', TestAttemptRetrieveUpdateDestroyView.as_view(), name='test-attempt-retrieve-update-destroy'),

    # FAQ URLs
    path('faqs/', FAQListCreateView.as_view(), name='faq-list-create'),
    path('faqs/<int:pk>/', FAQRetrieveUpdateDestroyView.as_view(), name='faq-retrieve-update-destroy'),

    # TestSettings URL
    path('test-settings/<int:test_id>/', TestSettingsView.as_view(), name='test-settings'),

    # Auth URLs
    path('login/', LoginView.as_view(), name='login'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('deactivate-account/', DeactivateAccountView.as_view(), name='deactivate-account'),

    # Include the router's URLs
    path('', include(router.urls)),  # This will include the admin-settings routes
]