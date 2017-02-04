from django import forms


class UploadFileForm(forms.Form):
    spotify_code = forms.CharField(widget=forms.CharField(attrs={'id': 'spotify-code'}), initial="This is the default spotify code")
    avatar_url = forms.CharField(widget=forms.CharField(attrs={'id': 'avatar-url'}), initial="/static/default.png")