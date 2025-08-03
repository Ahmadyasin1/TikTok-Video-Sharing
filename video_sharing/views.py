from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponseServerError

def custom_404(request, exception):
    """Custom 404 error handler"""
    return render(request, '404.html', {
        'request_path': request.get_full_path(),
        'user': request.user if hasattr(request, 'user') else None,
    }, status=404)

def custom_500(request):
    """Custom 500 error handler"""
    import uuid
    error_id = str(uuid.uuid4())[:8].upper()
    
    return render(request, '500.html', {
        'request_id': f'VS-{error_id}',
        'user': request.user if hasattr(request, 'user') else None,
    }, status=500)
