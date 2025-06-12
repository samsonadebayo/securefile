from pathlib import Path
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from dotenv import load_dotenv
from django.views import View 
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from datetime import timedelta, time
import logging
import os 

from .models import Profile, File
from .forms import ProfileForm, FileForm
 
# define base directory 
BASE_DIR = Path(__file__).resolve().parent.parent
# load env 
load_dotenv(dotenv_path=BASE_DIR/'.env')


User = get_user_model()
logger = logging.getLogger("users")


# home view 
def home_view(request):
	return render(request, 'home.html')


# profile view
@method_decorator(login_required(login_url='signin'), name='dispatch')
class ProfileView(View):

	def get(self, request):
		user = request.user
		profile = get_object_or_404(Profile, user=user)
		files = File.objects.filter(owner=user)
		return render(request, 'users/profile.html', {'user':user, 'profile':profile, 'files':files})


@login_required(login_url='signin')
def update_profile(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'users/profile_update.html', {'form': form})


# create file 
@login_required(login_url='signin')
def upload_file_view(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)  # <-- Add request.FILES
        if form.is_valid():
            file_instance = form.save(commit=False)
            file_instance.owner = request.user
            file_instance.save()
            messages.success(request, "File uploaded successfully")
            return redirect('profile')
        else:
            messages.error(request, "Invalid data")
            form.add_error(None, "Please correct the form errors")

    else:
        form = FileForm()

    return render(request, 'users/file_upload.html', {'form': form})


# file details 
@login_required(login_url='signin')
def file_detail(request, file_id):
    file = get_object_or_404(File, pk=file_id)
    return render(request, 'users/file.html', {'file': file})


# get file by token 
def get_file_view(request, pk):
	file = File.objects.filter(pk=pk).first()
	if file is None:
		messages.error(request, "File requestd does not exist")
		return redirect('home')

	return render(request, 'users/file.html', {'file':file})