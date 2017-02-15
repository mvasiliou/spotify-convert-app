from django.contrib import admin

# Register your models here.
from .models import UserProfile, AddedSong, MissedSong

admin.site.register(UserProfile)
admin.site.register(AddedSong)
admin.site.register(MissedSong)