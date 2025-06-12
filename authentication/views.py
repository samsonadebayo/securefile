from pathlib import Path
from django.views import View 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from dotenv import load_dotenv
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model, authenticate, logout, login
from django.contrib.auth.decorators import login_required
from datetime import timedelta, time
from datetime import datetime, date
import secrets 
import logging
import os 

from .forms import (
	SignupForm, SigninForm, ForgotPasswordForm, ResetPasswordForm,
	ChangePasswordForm, ChangeEmailForm
)


# define base directory 
BASE_DIR = Path(__file__).resolve().parent.parent
# load env 
load_dotenv(dotenv_path=BASE_DIR/'.env')

User = get_user_model()
logger = logging.getLogger("authentication")



# signup view 
class SignupView(View):

	# get request 
	def get(self, request):
		
		if request.user.is_authenticated:
			return redirect('profile')

		form = SignupForm()
		return render(request, 'auth/signup.html', {'form':form})

	# post request 
	def post(self, request):

		if request.user.is_authenticated:
			return redirect('profile')

		form = SignupForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']
			password = form.cleaned_data['password']

			try:
				# create user 
				user = User.objects.create(email=email)
				user.set_password(password)
				user.save()

				# create email verification token
				token = secrets.token_urlsafe(32)
				with transaction.atomic():
					user.email_verification_token = token
					user.email_verification_token_created_at = timezone.now()
					user.save(update_fields=["email_verification_token", "email_verification_token_created_at"])

				messages.success(request, "Account created successfully. Please check your email to verify your account. Remember to check your spam folder also")
				return redirect('signin')

			except Exception as e:
				logger.error(f": Error while creating new user account: {e}", exc_info=True)
				messages.error(request, "An unexpected error occurred. Please try again later")
				return render(request, 'auth/signup.html', {'form':form})
		else:
			messages.error(request, "Invalid data")
			form.add_error(None, "Please correct the form errors")

		return render(request, 'auth/signup.html', {'form':form})



# signin view 
class SigninView(View):

	# get request 
	def get(self, request):

		if request.user.is_authenticated:
			return redirect('profile')

		form = SigninForm()
		return render(request, 'auth/signin.html', {'form':form})

	# post request 
	def post(self, request):

		if request.user.is_authenticated:
			return redirect('profile')

		form = SigninForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']
			password = form.cleaned_data['password']

			# authenticate user 
			user = authenticate(request, email=email, password=password)
			# if user exists, check if user is disabled or is user is locked
			if user is not None:
				login(request, user)
				# log activity 
				logger.info(f": User {email} just logged in successfully")
				return redirect('profile')

				# notify user if account is locked 
				if user.is_locked:
					# log error
					logger.error(f": An unexpected error occurred while generating and saving activation code for {email}: {e}", exc_info=True)
					return redirect('signin')

			# if provided credentials matches no user 
			else:
				# check if the provided email exists and belongs to a user 
				user_account = User.objects.filter(email__iexact=email).first()
				if user_account is None:
					messages.error(request, "Incorrect signin credentials")
					return render(request, 'auth/signin.html', {'form':form})

				else:
					# measure time  
					time_since_last_failed_login = timedelta(hours=0)
					# check user last failed login 
					if user_account.last_failed_login is None or user_account.last_failed_login == time(0,0,0) and user_account.login_trials < 5:
						try:
							with transaction.atomic():
								user_account.login_trials += 1
								user_account.last_failed_login = timezone.now()
								user_account.save(update_fields=["login_trials", "last_failed_login"])
							messages.error(request, "Incorrect signin credentials")
							return redirect('signin')

						except Exception as e:
							# log error
							logger.error(f": An unexpected error occurred during atomic transaction on user_account: {e}", exc_info=True) 
							messages.error(request, "An unexpected error occurred. Please try again later")
							return redirect('signin')
					else:
						time_since_last_failed_login = timezone.now() - user_account.last_failed_login
						# check login trials 
						if user_account.login_trials >= 3:
							# compare time since last login to 24 hours 
							if time_since_last_failed_login >= timedelta(hours=24):
								try:
									with transaction.atomic():
										# set login trials to 1 and update last failed login
										user_account.login_trials = 1
										user_account.last_failed_login = timezone.now()
										user_account.save(update_fields=["login_trials", "last_failed_login"])

									messages.error(request, "Incorrect signin credentials")
									return redirect('signin')

								except Exception as e:
									# log error
									messages.error(request, "An unexpected error occurred. Please try again later")
									return redirect('signin')
							else:
								# calculate time left before account lockout is lifted 
								time_left = timedelta(hours=24) - time_since_last_failed_login
								try:
									# lock user account and update last failed login
									with transaction.atomic():
										user_account.last_failed_login = timezone.now()
										user_account.save(update_fields=["last_failed_login"])

									messages.error(request, f"Your account is temporarily locked for {time_left} due to too many failed login attempts.")
									return redirect('signin')

								except Exception as e:
									logger.error(f": An unexpected error occurred while locking user {user_account.email} account due to too many failed login attempt: {e}", exc_info=True)
									messages.error(request, "An unexpected error occurred. Please try again later")
									return redirect('signin')
						else:
							try:
								# increment login trials and update last failed login
								with transaction.atomic():
									user_account.login_trials += 1
									user_account.last_failed_login = timezone.now()
									user_account.save(update_fields=["login_trials", "last_failed_login"])

								messages.error(request, "Incorrect signin credentials")
								return redirect('signin')

							except Exception as e:
								# log error
								logger.error(f": An unexpected error occurred while updating user data after failed login: {e}", exc_info=True)
								messages.error(request, "An unexpected error occurred. Please try again later")
								return redirect('signin')

		else:
			messages.error(request, "Invalid data")
			form.add_error(None, "Please correct the form errors")

		return render(request, 'auth/signin.html', {'form':form})


# signout view 
@login_required(login_url='signin')
def signout_view(request):
	logout(request)
	return redirect('home')


# change password view 
@method_decorator(login_required(login_url='signin'), name='dispatch')
class ChangePasswordView(View):

	# get request 
	def get(self, request):
		form = ChangePasswordForm()
		return render(request, 'auth/change_password.html', {'form':form})

	# post request 
	def post(self, request):
		form = ChangePasswordForm(request.POST)
		if form.is_valid():

			try:
				new_password = form.cleaned_data['new_password']
				user = request.user
				with transaction.atomic():
					user.set_password(new_password)
					user.last_password_reset = timezone.now()
					user.save(update_fields=["password", "last_password_reset"])
				
				messages.success(request, "Password changed successfully")
				return redirect('profile')
			except  Exception as e:
				logger.error(f": An unexpected error occurred while changing user {user.email} password: {e}", exc_info=True)
				messages.error(request, "An unexpected error occurred")
				return redirect('profile')
		else:
			messages.error(request, "Invalid data")
			form.add_error(None, "Please correct the form errors")

		return render(request, 'auth/change_password.html', {'form':form})


# change email view 
@method_decorator(login_required(login_url='signin'), name='dispatch')
class ChangeEmailView(View):

	def get(self, request):
		form = ChangeEmailForm()
		return render(request, 'auth/change_email.html', {'form':form})

	def post(self, request):
		form = ChangeEmailForm(request.data)
		if form.is_valid():
			email = form.cleaned_data['new_email']
			user = request.user 
			user.email = email
			user.save()

			messages.success(request, "Email updated successfully")
			return redirect('profile')
		
		else:
			messages.error(request, "Invalid data")
			form.add_error(None, "Please correct the form errors")

		return render(request, 'auth/change_email.html', {'form':form})

