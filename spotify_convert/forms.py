from django import forms
from .models import UserProfile
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control'}))
    password = forms.CharField(widget = forms.PasswordInput(attrs = {'class' : 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'password')

class UserProfileForm(forms.ModelForm):
    email              = forms.EmailField(widget = forms.EmailInput(attrs={'id': 'email', 'class' : 'form-control'}))
    spotify_token      = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'spotify-token', 'class' : 'form-control'}))
    spotify_refresh    = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'spotify-refresh', 'class' : 'form-control'}))
    spotify_user_id    = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'spotify-user-id', 'class' : 'form-control'}))
    spotify_expires_at = forms.DateTimeField(widget=forms.HiddenInput(attrs={'id': 'spotify-expires-at', 'class' : 'form-control'}))
    display_name       = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'display-name', 'class' : 'form-control'}))
    class Meta:
        model = UserProfile
        fields = ('email', 'spotify_token','spotify_refresh','spotify_user_id','spotify_expires_at','display_name')

class UploadFileForm(forms.Form):
    file_url = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'file-url', 'class' : 'form-control'}), initial="")