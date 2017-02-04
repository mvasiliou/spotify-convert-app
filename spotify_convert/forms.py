from django import forms


class UploadFileForm(forms.Form):
    spotify_code = forms.CharField()
    avatar_url = forms.CharField()