from django.db import models

# Create your models here.
from django.db import models

class Spotify_User(models.Model):
    user_id = models.CharField(blank = False, max_length = 25)
    added_songs = models.ManyToManyField(Added_Songs)
    missed_songs = models.ManyToManyField(Missed_Songs)

class Added_Song(models.Model):
    spotify_user = models.ForeignKey(Spotify_User)
    apple_name = models.CharField(blank = False)
    apple_artist = models.CharField(blank=False)
    apple_id = models.CharField(blank=False)
    spotify_name = models.CharField(blank=False)
    spotify_id = models.CharField(blank=False)


class Missed_Song(models.Model):
    spotify_user = models.ForeignKey(Spotify_User)
    apple_name = models.CharField(blank=False)
    apple_artist = models.CharField(blank=False)
    apple_id = models.CharField(blank=False)


class Document(models.Model):
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)