from rest_framework import serializers
from .models import Video, Comment, Like
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class VideoSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 'video_file', 'thumbnail',
            'creator', 'uploaded_at', 'views_count', 'is_public',
            'tags', 'likes_count', 'comments_count'
        ]
        read_only_fields = ['uploaded_at', 'views_count', 'creator']
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_comments_count(self, obj):
        return obj.comments.count()


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'user', 'created_at', 'replies']
        read_only_fields = ['created_at', 'user']
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'created_at']
        read_only_fields = ['created_at', 'user']
