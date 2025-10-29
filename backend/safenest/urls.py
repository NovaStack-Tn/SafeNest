"""
URL configuration for SafeNest project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # JWT Authentication
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API endpoints
    path('api/', include('core.urls')),
    path('api/access-control/', include('access_control.urls')),
    path('api/security/', include('security.urls')),
    path('api/incidents/', include('incidents.urls')),
    path('api/faces/', include('faces.urls')),
    path('api/visitors/', include('visitor_assets.urls')),
    path('api/llm/', include('llm.urls')),
    path('api/dashboard/', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site
admin.site.site_header = 'SafeNest Administration'
admin.site.site_title = 'SafeNest Admin'
admin.site.index_title = 'Welcome to SafeNest Administration'
