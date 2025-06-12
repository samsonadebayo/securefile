import uuid
import os 
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# profile model 
class Profile(models.Model):
    fullname = models.CharField(max_length=80, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.user.email
    
    class Meta:
        ordering = ['-created_at']
 

class File(models.Model):
    filename = models.CharField(max_length=150, null=False, blank=False)
    file = models.FileField(upload_to="files/")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='file')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.filename}"