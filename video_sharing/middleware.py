import logging
import sys
from django.http import HttpResponse

logger = logging.getLogger(__name__)

class BrokenPipeMiddleware:
    """
    Middleware to handle broken pipe errors gracefully
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except BrokenPipeError:
            # Log the error but don't crash the server
            logger.warning(f"Broken pipe error for {request.path} from {request.META.get('REMOTE_ADDR', 'unknown')}")
            return HttpResponse("Connection closed by client", status=400)
        except Exception as e:
            # Log other exceptions
            logger.error(f"Error processing request {request.path}: {str(e)}")
            # Re-raise the exception to let Django handle it normally
            raise

class SecurityHeadersMiddleware:
    """
    Add security headers to all responses
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Add HSTS header for HTTPS (development only when needed)
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
