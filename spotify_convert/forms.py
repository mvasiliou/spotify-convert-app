from django import forms


class UploadFileForm(forms.Form):
    email = forms.EmailField(widget = forms.EmailInput(attrs={'id': 'email', 'class' : 'form-control'}))
    spotify_code = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'spotify-code', 'class' : 'form-control'}))
    file_url = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'file-url', 'class' : 'form-control'}), initial="")