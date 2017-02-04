from django import forms


class UploadFileForm(forms.Form):
    spotify_code = forms.CharField(widget=forms.HiddenInput, id="spotify-code", name='spotify-code', value="This is the default spotify code")
    avatar_url = forms.CharField(widget=forms.HiddenInput, id="avatar-url", name='avatar-url',value="/static/default.png")