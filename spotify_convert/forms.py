from django import forms


class UploadFileForm(forms.Form):
    spotify_code = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'spotify-code', 'class' : 'form-control'}))
    file_url = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'file-url', 'class' : 'form-control'}), initial="")