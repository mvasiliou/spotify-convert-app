from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UploadFileForm
from spotify_convert.tasks import go
import requests
from django.conf import settings
from django.core.files.storage import FileSystemStorage



# Create your views here.
def index(request):
    client_id = "fe7c45192a2944efb2141ef65cd40dbe"
    client_secret = "d1e8f5deb9af4ebf91b48c4c671d7203"

    callback = get_callback()
    spotify_url = "https://accounts.spotify.com/authorize?client_id=" + client_id + \
                  "&response_type=code&redirect_uri=" + \
                  callback + "&scope=user-library-modify+user-library-read"

    if request.method == 'POST':
        code = request.GET["code"]
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            print('Got File!')
            token, refresh = get_token(code, callback, client_id, client_secret)
            library = form.cleaned_data['file']
            fs = FileSystemStorage()
            filename = fs.save(library.name, library)
            uploaded_file_url = fs.url(filename)
            print(uploaded_file_url)

            go.delay(uploaded_file_url, token)
            return HttpResponseRedirect('/spotify_convert/')
        else:
            print('Form is not valid')
            print(form.errors)
    else:
        form = UploadFileForm()
        if "code" in request.GET:
            code = request.GET["code"]
            return render(request, 'spotify_convert/index.html', {'file_form':form, 'spotify_url': spotify_url,'code':code})
    return render(request, 'spotify_convert/index.html', {'file_form':form, 'spotify_url':spotify_url})


def get_callback():
    if settings.PRODUCTION:
        callback = "https%3A%2F%2Fshrouded-bastion-15188.herokuapp.com%2Fspotify_convert%2F"
    else:
        callback = "http%3A%2F%2F127.0.0.1%3A8000%2Fspotify_convert%2F"

    return callback

def get_token(code, callback, client_id, client_secret):
    params = {'grant_type':'authorization_code', 'code':code, 'redirect_uri':callback}

    req = requests.post(
            'https://accounts.spotify.com/api/token',
            data = params,
            auth = (client_id, client_secret)
        )
    data = req.json()
    token = data['access_token']
    refresh = data['refresh_token']
    return token, refresh

def user_login(request):
    context = RequestContext(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username = username, password = password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/spotify_convert/account/')
            else:
                return HttpResponse("Your War Room account is disabled")
        else:
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login credentials.")
    else:
        return render(request, 'spotify_convert/login.html', {}, context)

@login_required
def user_logout(request):
    logout(request)

    return HttpResponseRedirect('/spotify_convert/')