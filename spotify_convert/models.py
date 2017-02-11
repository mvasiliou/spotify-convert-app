from django.db import models

# Create your models here.
from django.db import models


class SpotifyUser(models.Model):
    user_id = models.CharField(blank = False, max_length = 50)

class AddedSong(models.Model):
    spotify_user = models.ForeignKey(SpotifyUser)
    apple_name = models.CharField(blank = False, max_length = 200)
    apple_artist = models.CharField(blank = False, max_length = 200)
    apple_id = models.CharField(blank = False, max_length = 200)
    spotify_name = models.CharField(blank = False, max_length = 200)
    spotify_id = models.CharField(blank = False, max_length = 100)

    def __str__(self):
        return str(self.apple_name + " by " + self.apple_artist)

class MissedSong(models.Model):
    spotify_user = models.ForeignKey(SpotifyUser)
    apple_name = models.CharField(blank = False, max_length = 200)
    apple_artist = models.CharField(blank = False, max_length = 200)
    apple_id = models.CharField(blank = False, max_length = 100)

    def __str__(self):
        return str(self.apple_name + " by " + self.apple_artist)