from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # JWT authentication routes (placed before the app's URLs to avoid conflicts)
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login for obtaining JWT token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Route for refreshing JWT token
    
    # Admin interface
    path('admin/', admin.site.urls),

    # Include the app's URL patterns under the /api/ path
    path('api/', include('newapp.urls')),  # Including the app's URL patterns
]
