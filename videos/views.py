from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from .models import Video, Comment, VideoRating
from .forms import VideoUploadForm, CommentForm, VideoSearchForm
import os

def dashboard(request):
    """Main dashboard showing latest videos"""
    search_form = VideoSearchForm(request.GET)
    videos = Video.objects.filter(is_active=True)
    
    # Search functionality
    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        genre = search_form.cleaned_data.get('genre')
        
        if query:
            videos = videos.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) |
                Q(creator__username__icontains=query)
            )
        
        if genre:
            videos = videos.filter(genre=genre)
    
    # Pagination
    paginator = Paginator(videos, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'videos': page_obj,
        'search_form': search_form,
        'total_videos': videos.count()
    }
    return render(request, 'dashboard.html', context)

def video_detail(request, video_id):
    """Detailed view of a single video"""
    video = get_object_or_404(Video, id=video_id, is_active=True)
    
    # Increment view count
    video.views += 1
    video.save(update_fields=['views'])
    
    # Get comments
    comments = video.comments.filter(is_active=True)[:10]
    
    # Handle comment submission
    comment_form = CommentForm()
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.video = video
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('videos:video_detail', video_id=video.id)
    
    # Get average rating
    avg_rating = video.ratings.aggregate(Avg('rating'))['rating__avg'] or 0
    user_rating = None
    if request.user.is_authenticated:
        user_rating = video.ratings.filter(user=request.user).first()
    
    context = {
        'video': video,
        'comments': comments,
        'comment_form': comment_form,
        'avg_rating': round(avg_rating, 1),
        'user_rating': user_rating,
    }
    return render(request, 'video_detail.html', context)

@login_required
def creator_upload(request):
    """Video upload page for creators only with enhanced validation"""
    if request.user.user_type != 'creator':
        messages.error(request, 'Only creators can upload videos. Please contact admin to upgrade your account.')
        return redirect('videos:dashboard')
    
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.creator = request.user
            
            # Enhanced file validation
            uploaded_file = request.FILES.get('video_file')
            if uploaded_file:
                # Check file size (max 100MB)
                if uploaded_file.size > 100 * 1024 * 1024:
                    messages.error(request, 'File size must be less than 100MB.')
                    return render(request, 'creator_upload.html', {'form': form})
                
                # Check file type
                allowed_types = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-msvideo']
                if uploaded_file.content_type not in allowed_types:
                    messages.error(request, 'Please upload a valid video file (MP4, AVI, MOV, WMV).')
                    return render(request, 'creator_upload.html', {'form': form})
                
                # Check file extension as backup
                import os
                file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                allowed_extensions = ['.mp4', '.avi', '.mov', '.wmv']
                if file_ext not in allowed_extensions:
                    messages.error(request, 'Please upload a valid video file with extension: MP4, AVI, MOV, WMV.')
                    return render(request, 'creator_upload.html', {'form': form})
                
                video.file_size = uploaded_file.size
            
            # Auto-generate some metadata
            video.views = 0
            video.likes = 0
            video.dislikes = 0
            
            try:
                video.save()
                messages.success(request, f'✅ Video "{video.title}" uploaded successfully!')
                return redirect('videos:video_detail', video_id=video.id)
            except Exception as e:
                messages.error(request, f'Error uploading video: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = VideoUploadForm()
    
    # Get user's video count for dashboard
    user_video_count = Video.objects.filter(creator=request.user).count()
    
    context = {
        'form': form,
        'user_video_count': user_video_count,
        'max_file_size': '100MB'
    }
    return render(request, 'creator_upload.html', context)

@login_required
@require_POST
def rate_video(request, video_id):
    """AJAX endpoint for rating videos"""
    video = get_object_or_404(Video, id=video_id)
    rating_value = int(request.POST.get('rating', 0))
    
    if 1 <= rating_value <= 5:
        rating, created = VideoRating.objects.update_or_create(
            video=video,
            user=request.user,
            defaults={'rating': rating_value}
        )
        
        # Calculate new average
        avg_rating = video.ratings.aggregate(Avg('rating'))['rating__avg'] or 0
        
        return JsonResponse({
            'success': True,
            'average_rating': round(avg_rating, 1),
            'user_rating': rating_value
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid rating'})

@login_required
def my_videos(request):
    """Show user's uploaded videos (creators only)"""
    if request.user.user_type != 'creator':
        messages.error(request, 'Access denied.')
        return redirect('videos:dashboard')
    
    videos = Video.objects.filter(creator=request.user, is_active=True)
    paginator = Paginator(videos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'my_videos.html', {'videos': page_obj})

def api_videos(request):
    """REST API endpoint for videos"""
    videos = Video.objects.filter(is_active=True)[:20]
    data = []
    
    for video in videos:
        data.append({
            'id': video.id,
            'title': video.title,
            'description': video.description,
            'creator': video.creator.username,
            'genre': video.genre,
            'age_rating': video.age_rating,
            'views': video.views,
            'likes': video.likes,
            'created_at': video.created_at.isoformat(),
            'video_url': video.video_url
        })
    
    return JsonResponse({'videos': data})
