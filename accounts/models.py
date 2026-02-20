from django.db import models
from django.contrib.auth.models import User
import os

def hotel_logo_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'hotel_{instance.user.id}_logo.{ext}'
    return os.path.join('hotel_logos', filename)

class Hotel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hotel')
    hotel_name = models.CharField(max_length=200)
    hotel_logo = models.ImageField(upload_to=hotel_logo_path, blank=True, null=True)
    mobile_number = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Hotel'
        verbose_name_plural = 'Hotels'
    
    def __str__(self):
        return self.hotel_name
    
    def get_logo_url(self):
        if self.hotel_logo:
            return self.hotel_logo.url
        return None