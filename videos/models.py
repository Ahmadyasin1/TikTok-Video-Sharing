from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
import os

User = get_user_model()

def video_upload_path(instance, filename):
    return f'videos/{instance.creator.username}/{filename}'

class Video(models.Model):
    GENRE_CHOICES = [
        ('comedy', 'Comedy'),
        ('music', 'Music'),
        ('education', 'Education'),
        ('entertainment', 'Entertainment'),
        ('news', 'News'),
        ('sports', 'Sports'),
        ('gaming', 'Gaming'),
        ('lifestyle', 'Lifestyle'),
    ]
    
    AGE_RATING_CHOICES = [
        ('G', 'General Audiences'),
        ('PG', 'Parental Guidance'),
        ('PG-13', 'Parents Strongly Cautioned'),
        ('R', 'Restricted'),
        ('18+', 'Adults Only'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='videos')
    publisher = models.CharField(max_length=100, blank=True)
    producer = models.CharField(max_length=100, blank=True)
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES)
    age_rating = models.CharField(max_length=5, choices=AGE_RATING_CHOICES)
    
    # File storage
    video_file = models.FileField(upload_to=video_upload_path, blank=True, null=True)
    external_url = models.URLField(blank=True, null=True)  # For external storage
    
    # Metadata
    duration = models.DurationField(blank=True, null=True)
    file_size = models.BigIntegerField(blank=True, null=True)
    
    # Engagement
    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def video_url(self):
        if self.video_file:
            return self.video_file.url
        return self.external_url
    
    def get_file_size_mb(self):
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0

class Comment(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.video.title}"

class VideoRating(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('video', 'user')
    
    def __str__(self):
        return f"{self.user.username} rated {self.video.title}: {self.rating}"
