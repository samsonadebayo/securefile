from django.urls import path 
from django.conf import settings
from django.conf.urls.static import static
from .views import (
	SignupView, SigninView, signout_view, ChangePasswordView, ChangeEmailView
)


urlpatterns = [
	path('signup/', SignupView.as_view(), name='signup'),
	path('signin/', SigninView.as_view(), name='signin'),
	path('signout/', signout_view, name='signout'),
	path('change_password/', ChangePasswordView.as_view(), name='change_password'),
	path('change_email/', ChangeEmailView.as_view(), name='change_email'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)