from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPES = (
        ('consumer', 'Consumer'),
        ('creator', 'Creator'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='consumer')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"
