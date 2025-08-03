from django.urls import path
from . import views
from .api_views import RegisterAPIView

app_name = 'users'

urlpatterns = [
    # Traditional Django views
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('subscriptions/', views.subscriptions_view, name='subscriptions'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    path('admin/database/', views.admin_database_view, name='admin_database'),
    path('admin/api/stats/', views.admin_api_stats, name='admin_api_stats'),
    
    # API endpoints for React frontend
    path('api/register/', RegisterAPIView.as_view(), name='api_register'),
]
