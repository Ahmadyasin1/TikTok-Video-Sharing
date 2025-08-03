from django.contrib import admin
from .models import Video, Comment, VideoRating

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'genre', 'age_rating', 'views', 'created_at', 'is_active']
    list_filter = ['genre', 'age_rating', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'creator__username']
    readonly_fields = ['views', 'created_at', 'updated_at', 'file_size']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'video', 'content_preview', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['content', 'user__username', 'video__title']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

@admin.register(VideoRating)
class VideoRatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'video', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'video__title']
