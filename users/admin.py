from django.contrib import admin
from .models import Profile, File


# profile admin
class ProfileAdmin(admin.ModelAdmin):
	list_display = ['fullname', 'user', 'created_at']
	list_display_links = ['fullname', 'user']

admin.site.register(Profile, ProfileAdmin)

# file admin 
class FileAdmin(admin.ModelAdmin):
	list_display = ['filename', 'file', 'owner', 'uploaded_at']
	list_display_links = ['filename', 'file']

admin.site.register(File, FileAdmin)
