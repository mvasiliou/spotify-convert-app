from django.db import models

# Create your models here.
from django.db import models

class Added_Song(models.Model):
    apple_name = models.CharField(blank = False, max_length = 200)
    apple_artist = models.CharField(blank=False, max_length = 200)
    apple_id = models.CharField(blank=False, max_length = 200)
    spotify_name = models.CharField(blank=False, max_length = 200)
    spotify_id = models.CharField(blank=False, max_length = 100)


class Missed_Song(models.Model):
    apple_name = models.CharField(blank=False, max_length = 200)
    apple_artist = models.CharField(blank=False, max_length = 200)
    apple_id = models.CharField(blank=False, max_length = 100)


class Spotify_User(models.Model):
    user_id = models.CharField(blank = False, max_length = 50)
    added_songs = models.ManyToManyField(Added_Song)
    missed_songs = models.ManyToManyField(Missed_Song)