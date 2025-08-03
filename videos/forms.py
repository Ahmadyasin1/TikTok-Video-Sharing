from django import forms
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from .models import Video, Comment
import os

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'description', 'publisher', 'producer', 'genre', 'age_rating', 'video_file', 'external_url']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'required': True,
                'placeholder': 'Enter video title...',
                'maxlength': 200
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Describe your video...',
                'maxlength': 1000
            }),
            'publisher': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Publisher name (optional)'
            }),
            'producer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Producer name (optional)'
            }),
            'genre': forms.Select(attrs={
                'class': 'form-control', 
                'required': True
            }),
            'age_rating': forms.Select(attrs={
                'class': 'form-control', 
                'required': True
            }),
            'video_file': forms.FileInput(attrs={
                'class': 'form-control', 
                'accept': 'video/*',
                'id': 'video-upload'
            }),
            'external_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Or provide external video URL'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['video_file'].validators.append(
            FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov', 'wmv'])
        )
        self.fields['video_file'].help_text = "Upload MP4, AVI, MOV, or WMV files (max 100MB)"
        self.fields['external_url'].help_text = "Alternative to file upload - provide direct video URL"
    
    def clean_video_file(self):
        video_file = self.cleaned_data.get('video_file')
        if video_file:
            # Check file size (100MB limit)
            if video_file.size > 100 * 1024 * 1024:
                raise ValidationError("File size cannot exceed 100MB.")
            
            # Check file extension
            ext = os.path.splitext(video_file.name)[1].lower()
            allowed_extensions = ['.mp4', '.avi', '.mov', '.wmv']
            if ext not in allowed_extensions:
                raise ValidationError("Please upload a valid video file (MP4, AVI, MOV, WMV).")
            
            # Basic content type check
            allowed_content_types = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-msvideo']
            if hasattr(video_file, 'content_type') and video_file.content_type:
                if video_file.content_type not in allowed_content_types:
                    raise ValidationError("Invalid video file type. Please upload MP4, AVI, MOV, or WMV.")
        
        return video_file
    
    def clean_external_url(self):
        external_url = self.cleaned_data.get('external_url')
        if external_url:
            # Basic URL validation
            if not external_url.startswith(('http://', 'https://')):
                raise ValidationError("Please provide a valid URL starting with http:// or https://")
            
            # Check if URL points to a video file
            video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.webm', '.mkv']
            if not any(external_url.lower().endswith(ext) for ext in video_extensions):
                # Allow if it's a common video hosting platform
                allowed_domains = ['youtube.com', 'vimeo.com', 'dailymotion.com', 'twitch.tv']
                if not any(domain in external_url.lower() for domain in allowed_domains):
                    raise ValidationError("URL should point to a video file or be from a supported platform.")
        
        return external_url
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title:
            title = title.strip()
            if len(title) < 3:
                raise ValidationError("Title must be at least 3 characters long.")
            if len(title) > 200:
                raise ValidationError("Title cannot exceed 200 characters.")
        return title
    
    def clean(self):
        cleaned_data = super().clean()
        video_file = cleaned_data.get('video_file')
        external_url = cleaned_data.get('external_url')
        
        if not video_file and not external_url:
            raise ValidationError("Please either upload a video file or provide an external URL.")
        
        if video_file and external_url:
            raise ValidationError("Please provide either a video file OR an external URL, not both.")
        
        return cleaned_data

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add a comment...'})
        }

class VideoSearchForm(forms.Form):
    query = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search videos...'})
    )
    genre = forms.ChoiceField(
        choices=[('', 'All Genres')] + Video.GENRE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
