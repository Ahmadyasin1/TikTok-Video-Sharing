from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth import get_user_model
from videos.models import Video, Comment, VideoRating
from videos.forms import VideoUploadForm
import json
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class BaseAPIView(View):
    """Base API view with common functionality"""
    
    def dispatch(self, request, *args, **kwargs):
        # Add CORS headers
        response = super().dispatch(request, *args, **kwargs)
        if hasattr(response, 'headers'):
            response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Allow-Headers'] = 'X-CSRFToken, Content-Type, Authorization'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        return response
    
    def options(self, request, *args, **kwargs):
        """Handle CORS preflight requests"""
        response = JsonResponse({'status': 'ok'})
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Headers'] = 'X-CSRFToken, Content-Type, Authorization'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        return response

class VideosAPIView(BaseAPIView):
    """API endpoint for videos"""
    
    def get(self, request):
        """Get videos with optional filtering"""
        try:
            # Get query parameters
            query = request.GET.get('query', '')
            genre = request.GET.get('genre', '')
            page = int(request.GET.get('page', 1))
            per_page = int(request.GET.get('per_page', 12))
            
            # Start with active videos
            videos = Video.objects.filter(is_active=True).select_related('creator')
            
            # Apply filters
            if query:
                videos = videos.filter(
                    Q(title__icontains=query) | 
                    Q(description__icontains=query) |
                    Q(creator__username__icontains=query)
                )
            
            if genre:
                videos = videos.filter(genre=genre)
            
            # Order by most recent
            videos = videos.order_by('-created_at')
            
            # Paginate
            paginator = Paginator(videos, per_page)
            page_obj = paginator.get_page(page)
            
            # Serialize videos
            videos_data = []
            for video in page_obj:
                video_data = {
                    'id': video.id,
                    'title': video.title,
                    'description': video.description,
                    'creator': video.creator.username,
                    'genre': video.genre,
                    'age_rating': video.age_rating,
                    'views': video.views,
                    'likes': video.likes,
                    'dislikes': video.dislikes,
                    'average_rating': float(video.average_rating or 0),
                    'comments_count': video.comment_set.count(),
                    'created_at': video.created_at.isoformat(),
                    'video_url': video.video_file.url if video.video_file else video.external_url,
                    'thumbnail': None  # Add thumbnail logic if needed
                }
                videos_data.append(video_data)
            
            return JsonResponse({
                'success': True,
                'videos': videos_data,
                'pagination': {
                    'current_page': page_obj.number,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                }
            })
            
        except Exception as e:
            logger.error(f"Error in VideosAPIView.get: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to fetch videos'
            }, status=500)

class VideoDetailAPIView(BaseAPIView):
    """API endpoint for video details"""
    
    def get(self, request, video_id):
        """Get detailed video information"""
        try:
            video = Video.objects.select_related('creator').get(
                id=video_id, 
                is_active=True
            )
            
            # Increment view count
            video.views += 1
            video.save(update_fields=['views'])
            
            # Get comments
            comments = Comment.objects.filter(video=video).select_related('user').order_by('-created_at')[:10]
            comments_data = [
                {
                    'id': comment.id,
                    'content': comment.content,
                    'user': comment.user.username,
                    'created_at': comment.created_at.isoformat(),
                    'avatar': None  # Add avatar logic if needed
                }
                for comment in comments
            ]
            
            # Get user's rating if authenticated
            user_rating = None
            if request.user.is_authenticated:
                try:
                    rating = VideoRating.objects.get(video=video, user=request.user)
                    user_rating = rating.rating
                except VideoRating.DoesNotExist:
                    pass
            
            video_data = {
                'id': video.id,
                'title': video.title,
                'description': video.description,
                'creator': {
                    'username': video.creator.username,
                    'user_type': video.creator.user_type,
                    'avatar': None  # Add avatar logic if needed
                },
                'genre': video.genre,
                'age_rating': video.age_rating,
                'views': video.views,
                'likes': video.likes,
                'dislikes': video.dislikes,
                'average_rating': float(video.average_rating or 0),
                'user_rating': user_rating,
                'comments_count': video.comment_set.count(),
                'created_at': video.created_at.isoformat(),
                'video_url': video.video_file.url if video.video_file else video.external_url,
                'thumbnail': None,
                'comments': comments_data
            }
            
            return JsonResponse({
                'success': True,
                'video': video_data
            })
            
        except Video.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Video not found'
            }, status=404)
        except Exception as e:
            logger.error(f"Error in VideoDetailAPIView.get: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to fetch video details'
            }, status=500)

class AuthAPIView(BaseAPIView):
    """API endpoint for authentication"""
    
    def post(self, request):
        """Handle login/logout"""
        try:
            data = json.loads(request.body)
            action = data.get('action')
            
            if action == 'login':
                username = data.get('username')
                password = data.get('password')
                
                if not username or not password:
                    return JsonResponse({
                        'success': False,
                        'error': 'Username and password required'
                    }, status=400)
                
                user = authenticate(request, username=username, password=password)
                if user:
                    login(request, user)
                    return JsonResponse({
                        'success': True,
                        'message': 'Login successful',
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'user_type': user.user_type,
                            'is_staff': user.is_staff
                        }
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid credentials'
                    }, status=401)
            
            elif action == 'logout':
                logout(request)
                return JsonResponse({
                    'success': True,
                    'message': 'Logout successful'
                })
            
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid action'
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Error in AuthAPIView.post: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Authentication failed'
            }, status=500)

class UserStatusAPIView(BaseAPIView):
    """API endpoint for user status"""
    
    def get(self, request):
        """Get current user status"""
        if request.user.is_authenticated:
            return JsonResponse({
                'success': True,
                'authenticated': True,
                'user': {
                    'id': request.user.id,
                    'username': request.user.username,
                    'email': request.user.email,
                    'user_type': request.user.user_type,
                    'is_staff': request.user.is_staff
                }
            })
        else:
            return JsonResponse({
                'success': True,
                'authenticated': False,
                'user': None
            })

class CSRFTokenAPIView(BaseAPIView):
    """API endpoint for CSRF token"""
    
    def get(self, request):
        """Get CSRF token"""
        token = get_token(request)
        return JsonResponse({
            'success': True,
            'csrfToken': token
        })

@method_decorator(csrf_exempt, name='dispatch')
class UploadAPIView(BaseAPIView):
    """API endpoint for video upload"""
    
    @method_decorator(login_required)
    def post(self, request):
        """Handle video upload"""
        try:
            # Check if user is a creator
            if request.user.user_type != 'creator':
                return JsonResponse({
                    'success': False,
                    'error': 'Only creators can upload videos'
                }, status=403)
            
            form = VideoUploadForm(request.POST, request.FILES)
            if form.is_valid():
                video = form.save(commit=False)
                video.creator = request.user
                
                # Enhanced file validation (already handled in views.py)
                uploaded_file = request.FILES.get('video_file')
                if uploaded_file:
                    # File validation
                    if uploaded_file.size > 100 * 1024 * 1024:
                        return JsonResponse({
                            'success': False,
                            'error': 'File size must be less than 100MB'
                        }, status=400)
                    
                    # Check file extension
                    import os
                    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                    allowed_extensions = ['.mp4', '.avi', '.mov', '.wmv']
                    if file_ext not in allowed_extensions:
                        return JsonResponse({
                            'success': False,
                            'error': 'Please upload a valid video file (MP4, AVI, MOV, WMV)'
                        }, status=400)
                    
                    video.file_size = uploaded_file.size
                
                # Set initial values
                video.views = 0
                video.likes = 0
                video.dislikes = 0
                
                video.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Video uploaded successfully',
                    'video_id': video.id
                })
            else:
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = [str(error) for error in error_list]
                
                return JsonResponse({
                    'success': False,
                    'error': 'Validation failed',
                    'errors': errors
                }, status=400)
                
        except Exception as e:
            logger.error(f"Error in UploadAPIView.post: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Upload failed'
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class RatingAPIView(BaseAPIView):
    """API endpoint for video rating"""
    
    @method_decorator(login_required)
    def post(self, request, video_id):
        """Rate a video"""
        try:
            data = json.loads(request.body)
            rating_value = data.get('rating')
            
            if not rating_value or not (1 <= int(rating_value) <= 5):
                return JsonResponse({
                    'success': False,
                    'error': 'Rating must be between 1 and 5'
                }, status=400)
            
            video = Video.objects.get(id=video_id, is_active=True)
            
            # Create or update rating
            rating, created = VideoRating.objects.update_or_create(
                video=video,
                user=request.user,
                defaults={'rating': int(rating_value)}
            )
            
            # Recalculate average rating
            avg_rating = VideoRating.objects.filter(video=video).aggregate(
                avg=Avg('rating')
            )['avg']
            
            video.average_rating = avg_rating
            video.save(update_fields=['average_rating'])
            
            return JsonResponse({
                'success': True,
                'user_rating': rating.rating,
                'average_rating': float(avg_rating or 0),
                'total_ratings': VideoRating.objects.filter(video=video).count()
            })
            
        except Video.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Video not found'
            }, status=404)
        except Exception as e:
            logger.error(f"Error in RatingAPIView.post: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Rating failed'
            }, status=500)
