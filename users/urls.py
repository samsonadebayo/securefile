from django.urls import path 
from django.conf import settings
from django.conf.urls.static import static
from .views import ProfileView, upload_file_view, get_file_view, update_profile, file_detail

urlpatterns = [
	path('profile/', ProfileView.as_view(), name='profile'),
	path('upload_file/', upload_file_view, name='upload_file'),
	path('files/<int:file_id>/', file_detail, name='file_detail'),
    path('update_profile/', update_profile, name='update_profile'),
	path('file/<int:pk>/', get_file_view, name='get_file'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)