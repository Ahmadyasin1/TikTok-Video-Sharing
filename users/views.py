from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.db import models
from django.utils import timezone
from videos.models import Video, VideoRating, Comment

User = get_user_model()

def is_admin(user):
    """Check if user is admin/superuser"""
    return user.is_superuser or user.is_staff

class CustomUserCreationForm(UserCreationForm):
    user_type = forms.ChoiceField(
        choices=[('consumer', 'Consumer'), ('creator', 'Creator')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'user_type', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email

def register_view(request):
    if request.user.is_authenticated:
        return redirect('videos:dashboard')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Registration successful!')
            return redirect('videos:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('videos:dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Please provide both username and password.')
            return render(request, 'login.html')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', 'videos:dashboard')
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

@login_required
def logout_view(request):
    username = request.user.username
    logout(request)
    messages.success(request, f'Goodbye {username}! You have been logged out.')
    return redirect('videos:dashboard')

@login_required
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})

@login_required
def subscriptions_view(request):
    """View for user subscriptions - for future implementation"""
    context = {
        'subscriptions': [],  # Placeholder for future subscription functionality
        'message': 'Subscription feature coming soon!'
    }
    return render(request, 'subscriptions.html', context)

@login_required
def edit_profile_view(request):
    """View for editing user profile"""
    if request.method == 'POST':
        # Handle profile updates
        user = request.user
        username = request.POST.get('username')
        email = request.POST.get('email')
        user_type = request.POST.get('user_type')
        
        if username and username != user.username:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists!')
            else:
                user.username = username
        
        if email:
            user.email = email
            
        if user_type in ['consumer', 'creator']:
            user.user_type = user_type
            
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('users:profile')
    
    return render(request, 'edit_profile.html', {'user': request.user})

@user_passes_test(is_admin)
def admin_database_view(request):
    """Admin-only view to see database statistics and management"""
    # Get statistics
    total_users = User.objects.count()
    total_creators = User.objects.filter(user_type='creator').count()
    total_consumers = User.objects.filter(user_type='consumer').count()
    total_videos = Video.objects.count()
    total_ratings = VideoRating.objects.count()
    total_comments = Comment.objects.count()
    
    # Recent activity
    recent_users = User.objects.order_by('-date_joined')[:10]
    recent_videos = Video.objects.order_by('-created_at')[:10]
    recent_comments = Comment.objects.order_by('-created_at')[:10]
    
    # Video statistics
    videos_by_genre = {}
    for genre_code, genre_name in Video.GENRE_CHOICES:
        count = Video.objects.filter(genre=genre_code).count()
        videos_by_genre[genre_name] = count
    
    context = {
        'stats': {
            'total_users': total_users,
            'total_creators': total_creators,
            'total_consumers': total_consumers,
            'total_videos': total_videos,
            'total_ratings': total_ratings,
            'total_comments': total_comments,
        },
        'recent_users': recent_users,
        'recent_videos': recent_videos,
        'recent_comments': recent_comments,
        'videos_by_genre': videos_by_genre,
    }
    
    return render(request, 'admin_database.html', context)

@staff_member_required
def admin_api_stats(request):
    """API endpoint for admin statistics"""
    if request.method == 'GET':
        stats = {
            'users': {
                'total': User.objects.count(),
                'creators': User.objects.filter(user_type='creator').count(),
                'consumers': User.objects.filter(user_type='consumer').count(),
                'active_today': User.objects.filter(last_login__date=timezone.now().date()).count(),
            },
            'videos': {
                'total': Video.objects.count(),
                'active': Video.objects.filter(is_active=True).count(),
                'total_views': Video.objects.aggregate(total_views=models.Sum('views'))['total_views'] or 0,
            },
            'engagement': {
                'total_ratings': VideoRating.objects.count(),
                'total_comments': Comment.objects.count(),
                'avg_rating': VideoRating.objects.aggregate(avg=models.Avg('rating'))['avg'] or 0,
            }
        }
        return JsonResponse(stats)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
