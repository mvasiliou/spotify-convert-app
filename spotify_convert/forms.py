from django import forms


class UploadFileForm(forms.Form):
    spotify_code = forms.CharField(widget=forms.HiddenInput, id="spotify-code", name='spotify-code', initial="This is the default spotify code")
    avatar_url = forms.CharField(widget=forms.HiddenInput, id="avatar-url", name='avatar-url',initial="/static/default.png")