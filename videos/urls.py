from django.urls import path
from . import views
from .api_views import (
    VideosAPIView, 
    VideoDetailAPIView, 
    AuthAPIView, 
    UserStatusAPIView, 
    CSRFTokenAPIView,
    UploadAPIView,
    RatingAPIView
)

app_name = 'videos'

urlpatterns = [
    # Traditional Django views
    path('', views.dashboard, name='dashboard'),
    path('video/<int:video_id>/', views.video_detail, name='video_detail'),
    path('upload/', views.creator_upload, name='creator_upload'),
    path('my-videos/', views.my_videos, name='my_videos'),
    path('rate/<int:video_id>/', views.rate_video, name='rate_video'),
    
    # API endpoints for React frontend
    path('api/videos/', VideosAPIView.as_view(), name='api_videos_list'),
    path('api/videos/<int:video_id>/', VideoDetailAPIView.as_view(), name='api_video_detail'),
    path('api/auth/', AuthAPIView.as_view(), name='api_auth'),
    path('api/user-status/', UserStatusAPIView.as_view(), name='api_user_status'),
    path('api/csrf-token/', CSRFTokenAPIView.as_view(), name='api_csrf_token'),
    path('api/upload/', UploadAPIView.as_view(), name='api_upload'),
    path('api/rate/<int:video_id>/', RatingAPIView.as_view(), name='api_rate_video'),
    
    # Legacy API endpoint (keep for backward compatibility)
    path('api/videos/', views.api_videos, name='api_videos_legacy'),
]
