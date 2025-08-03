from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views import View
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
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

@method_decorator(csrf_exempt, name='dispatch')
class RegisterAPIView(BaseAPIView):
    """API endpoint for user registration"""
    
    def post(self, request):
        """Handle user registration"""
        try:
            data = json.loads(request.body)
            
            # Extract data
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            user_type = data.get('user_type', 'consumer')
            password1 = data.get('password1', '')
            password2 = data.get('password2', '')
            
            # Validation
            errors = {}
            
            if not username:
                errors['username'] = ['Username is required']
            elif len(username) < 3:
                errors['username'] = ['Username must be at least 3 characters long']
            elif User.objects.filter(username=username).exists():
                errors['username'] = ['Username already exists']
            
            if not email:
                errors['email'] = ['Email is required']
            elif User.objects.filter(email=email).exists():
                errors['email'] = ['Email already exists']
            
            if user_type not in ['creator', 'consumer']:
                errors['user_type'] = ['Invalid user type']
            
            if not password1:
                errors['password1'] = ['Password is required']
            elif len(password1) < 8:
                errors['password1'] = ['Password must be at least 8 characters long']
            
            if password1 != password2:
                errors['password2'] = ['Passwords do not match']
            
            # Django password validation
            if password1 and not errors.get('password1'):
                try:
                    validate_password(password1)
                except ValidationError as e:
                    errors['password1'] = list(e.messages)
            
            if errors:
                return JsonResponse({
                    'success': False,
                    'error': 'Validation failed',
                    'errors': errors
                }, status=400)
            
            # Create user
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    user_type=user_type
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Registration successful',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'user_type': user.user_type
                    }
                })
                
            except Exception as e:
                logger.error(f"Error creating user: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to create user'
                }, status=500)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Error in RegisterAPIView.post: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Registration failed'
            }, status=500)
