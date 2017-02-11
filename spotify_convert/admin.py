from django.contrib import admin

# Register your models here.
from .models import SpotifyUser, AddedSong, MissedSong

admin.site.register(SpotifyUser)
admin.site.register(AddedSong)
admin.site.register(MissedSong)