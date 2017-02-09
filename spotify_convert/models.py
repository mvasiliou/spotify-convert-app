from django.db import models

# Create your models here.
from django.db import models


class Spotify_User(models.Model):
    user_id = models.CharField(blank = False, max_length = 50)

class Added_Song(models.Model):
    spotify_user = models.ForeignKey(Spotify_User)
    apple_name = models.CharField(blank = False, max_length = 200)
    apple_artist = models.CharField(blank = False, max_length = 200)
    apple_id = models.CharField(blank = False, max_length = 200)
    spotify_name = models.CharField(blank = False, max_length = 200)
    spotify_id = models.CharField(blank = False, max_length = 100)

class Missed_Song(models.Model):
    spotify_user = models.ForeignKey(Spotify_User)
    apple_name = models.CharField(blank = False, max_length = 200)
    apple_artist = models.CharField(blank = False, max_length = 200)
    apple_id = models.CharField(blank = False, max_length = 100)