from django import forms
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.forms import DateTimeInput

from .models import Profile, File

User = get_user_model()

# file form 
class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['filename', 'file']

    def clean_file(self):
        uploaded_file = self.cleaned_data.get('file')

        # 100MB limit (100 * 1024 * 1024 bytes)
        max_size = 100 * 1024 * 1024

        if uploaded_file and uploaded_file.size > max_size:
            raise forms.ValidationError("File size must not exceed 100MB.")

        return uploaded_file


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['fullname']
        widgets = {
            'fullname': forms.TextInput(attrs={'placeholder': 'Enter your full name'})
        }