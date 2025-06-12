from django import forms
from django.contrib.auth import get_user_model
import re

User = get_user_model()


# Signup form
class SignupForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput, required=True)
	password_again = forms.CharField(widget=forms.PasswordInput, required=True)

	class Meta:
		model = User
		fields = ['email', 'password', 'password_again']
		
	def clean_email(self):
		value = self.cleaned_data.get('email')
		errors = []

		if not value or value.isspace():
			errors.append("Email is required")
		if value and (len(value) < 6 or len(value) > 80):
			errors.append("Invalid email length. Email should be at least 6 characters, and not more than 80 characters")
		if value and User.objects.filter(email__iexact=value).exists():
			errors.append(f"Email {value} is unavailable")

		if errors:
			raise forms.ValidationError(errors)
		return value


	def clean(self):
		cleaned_data = super().clean()
		password = cleaned_data.get('password')
		password_again = cleaned_data.get('password_again')
		errors = {}

		if not password or password.isspace():
			errors.setdefault("password", []).append("Password is required")
		else:
			if len(password) < 8 or len(password) > 128:
				errors.setdefault("password", []).append("Password must be between 8 and 128 characters")
			if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
				errors.setdefault("password", []).append("Password must contain at least one special character")
			if not any(p.isdigit() for p in password):
				errors.setdefault("password", []).append("Password must contain at least one digit")
			if not any(p.islower() for p in password):
				errors.setdefault("password", []).append("Password must contain at least one lowercase")
			if not any(p.isupper() for p in password):
				errors.setdefault("password", []).append("Password must contain at least one uppercase")

		if password_again != password:
			errors.setdefault("password_again", []).append("Passwords do not match")

		if errors:
			raise forms.ValidationError(errors)

		return cleaned_data


# Signin form
class SigninForm(forms.Form):
	email = forms.EmailField(required=True, min_length=6, max_length=60)
	password = forms.CharField(widget=forms.PasswordInput, required=True)


# Change Password form
class ChangePasswordForm(forms.Form):
	old_password = forms.CharField(widget=forms.PasswordInput, required=True)
	new_password = forms.CharField(widget=forms.PasswordInput, required=True)
	new_password_again = forms.CharField(widget=forms.PasswordInput, required=True)

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super(ChangePasswordForm, self).__init__(*args, **kwargs)

	def clean(self):
		cleaned_data = super().clean()
		old_password = cleaned_data.get('old_password')
		new_password = cleaned_data.get('new_password')
		new_password_again = cleaned_data.get('new_password_again')

		errors = {}

		# Old password checks
		if not self.user or not self.user.check_password(old_password):
			errors.setdefault('old_password', []).append("Old password is incorrect")

		# New password checks
		if new_password is None or new_password.isspace():
			errors.setdefault('new_password', []).append("New password is required")
		else:
			if len(new_password) < 8:
				errors.setdefault('new_password', []).append("Password must be at least 8 characters")
			if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", new_password):
				errors.setdefault('new_password', []).append("Password must contain at least one special character")
			if not any(p.isdigit() for p in new_password):
				errors.setdefault('new_password', []).append("Password must contain at least one digit")
			if not any(p.islower() for p in new_password):
				errors.setdefault('new_password', []).append("Password must contain at least one lowercase letter")
			if not any(p.isupper() for p in new_password):
				errors.setdefault('new_password', []).append("Password must contain at least one uppercase letter")
			if old_password and new_password == old_password:
				errors.setdefault('new_password', []).append("You cannot use the same password as your old password")

		# Confirm password check
		if new_password_again != new_password:
			errors.setdefault('new_password_again', []).append("Both fields for new password must match")

		if errors:
			raise forms.ValidationError(errors)

		return cleaned_data



# Forgot Password form
class ForgotPasswordForm(forms.Form):
	email = forms.EmailField(required=True, min_length=6, max_length=60)

	def clean_email(self):
		value = self.cleaned_data.get('email')
		errors = []

		if not value or value.isspace():
			errors.append("Please provide a valid email")
		if value and (len(value) < 6 or len(value) > 60):
			errors.append("Email can only be between 6 to 60 characters")
		if value and not User.objects.filter(email__iexact=value).exists():
			errors.append(f"Can't find account with email {value}")

		if errors:
			raise forms.ValidationError(errors)

		return value



# Reset Password form
class ResetPasswordForm(forms.Form):
	new_password = forms.CharField(widget=forms.PasswordInput, required=True)
	new_password_again = forms.CharField(widget=forms.PasswordInput, required=True)

	def clean(self):
		cleaned_data = super().clean()
		new_password = cleaned_data.get('new_password')
		new_password_again = cleaned_data.get('new_password_again')
		errors = {}

		if not new_password or new_password.isspace():
			errors['password'] = "New password is required"
		if len(new_password) < 8:
			errors["password"] = "Password must be at least 8 characters"
		if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", new_password):
			errors["password"] = "Password must contain at least one special character"
		if not any(p.isdigit() for p in new_password):
			errors["password"] = "Password must contain at least one digit"
		if not any(p.islower() for p in new_password):
			errors["password"] = "Password must contain at least one lowercase"
		if not any(p.isupper() for p in new_password):
			errors["password"] = "Password must contain at least one uppercase"
		if new_password_again != new_password:
			errors["password"] = "New passwords must match"

		if errors:
			raise forms.ValidationError(errors)


# Change email form
class ChangeEmailForm(forms.Form):
	new_email = forms.EmailField(max_length=80, required=True)

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super(ChangeEmailForm, self).__init__(*args, **kwargs)

	def clean_new_email(self):
		value = self.cleaned_data.get('new_email')
		errors = []

		if not value or value.isspace():
			errors.append("Email is required")
		if value and (len(value) < 6 or len(value) > 80):
			errors.append("Invalid email length. Email should be at least 6 characters and not more than 80 characters")
		if self.user and value != self.user.email and User.objects.filter(email__iexact=value).exists():
			errors.append(f"Email {value} is unavailable")

		if errors:
			raise forms.ValidationError(errors)
		return value


# User form (for read/write model data)
class UserForm(forms.ModelForm):
	class Meta:
		model = User
		fields = '__all__'