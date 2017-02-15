from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User,null=True)
    email = models.CharField(max_length = 200, null = False)
    spotify_user_id = models.CharField(blank = False, max_length = 500)
    spotify_token = models.CharField(blank = False, max_length = 500)
    spotify_refresh = models.CharField(blank = False, max_length = 500)
    display_name = models.CharField(blank = False, max_length = 500)
    def __str__(self):
        return str(self.email)

class AddedSong(models.Model):
    spotify_user = models.ForeignKey(UserProfile)
    apple_name = models.CharField(blank = False, max_length = 200)
    apple_artist = models.CharField(blank = False, max_length = 200)
    apple_id = models.CharField(blank = False, max_length = 200)
    spotify_name = models.CharField(blank = False, max_length = 200)
    spotify_id = models.CharField(blank = False, max_length = 100)

    def __str__(self):
        return str(self.apple_name + " by " + self.apple_artist)

class MissedSong(models.Model):
    spotify_user = models.ForeignKey(UserProfile)
    apple_name = models.CharField(blank = False, max_length = 200)
    apple_artist = models.CharField(blank = False, max_length = 200)
    apple_id = models.CharField(blank = False, max_length = 100)

    def __str__(self):
        return str(self.apple_name + " by " + self.apple_artist)