from django import forms


class UploadFileForm(forms.Form):
    spotify_code = forms.CharField(widget=forms.TextInput(attrs={'id': 'spotify-code'}), initial="This is the default spotify code")
    avatar_url = forms.CharField(widget=forms.TextInput(attrs={'id': 'avatar-url'}), initial="/static/default.png")