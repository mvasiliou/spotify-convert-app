from django.contrib import admin

# Register your models here.
from .models import Spotify_User, Added_Song, Missed_Song

admin.site.register(Spotify_User)
admin.site.register(Added_Song)
admin.site.register(Missed_Song)