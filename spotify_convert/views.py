from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UploadFileForm, UserProfileForm, UserForm
from spotify_convert.tasks import go, get_token
import json, boto3, os
import spotify_convert.helper as helper
from django.conf import settings
from .models import UserProfile
import spotipy
from pprint import pprint
import datetime

# Create your views here.
def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/spotify_convert/convert/')
    else:
        client_id = os.environ.get('SPOTIFY_CLIENT_ID')
        callback = helper.get_callback()
        spotify_url = "https://accounts.spotify.com/authorize?client_id=" + client_id + \
                        "&response_type=code&redirect_uri=" + \
                        callback + "&scope=user-library-modify+user-library-read"
        context = {'spotify_url':spotify_url}
        return render(request, 'spotify_convert/index.html', context)


def convert(request):
    if request.user.is_authenticated():
        file_form = UploadFileForm()
        context = {'file_form': file_form}
        return render(request, 'spotify_convert/convert.html', context)
    else:
        return HttpResponseRedirect('/spotify_convert/register')

def complete(request):
    return render(request,'spotify_convert/complete.html',{})

def sign_s3(request):
    S3_BUCKET = os.environ.get('S3_BUCKET_NAME')
    file_name = request.GET['file_name']
    file_type = request.GET['file_type']

    s3 = boto3.client('s3')

    presigned_post = s3.generate_presigned_post(
        Bucket = S3_BUCKET,
        Key = file_name,
        Fields = {"acl": "private", "Content-Type": file_type},
        Conditions = [
            {"acl": "private"},
            {"Content-Type": file_type}
        ],
        ExpiresIn = 3600
    )
    json_output = json.dumps({'data': presigned_post,
                              'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
                            })
    return HttpResponse(json_output, content_type = "application/json")


def submit_form(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            form = UploadFileForm(request.POST)
            if form.is_valid():
                library_url = form.cleaned_data['file_url']
                go.delay(library_url, request.user)
                return HttpResponseRedirect('/spotify_convert/complete/')
            else:
                print('Form is not valid')
                print(form.errors)
        else:
            form = UploadFileForm()
        return HttpResponseRedirect('/spotify_convert/complete/')


def register(request):
    registered = False
    context = {}
    if request.method == 'POST':
        profile_form = UserProfileForm(data = request.POST)
        user_form = UserForm(data = request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            username = user.username
            password = user.password
            user.set_password(password)
            user.save()

            profile = profile_form.save(commit = False)
            profile.user = user
            profile.save()
            registered = True

            user = authenticate(username = username, password = password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/spotify_convert/convert/')
            else:
                #Send to a login page if it didn't work later 
                return HttpResponseRedirect('/spotify_convert/login/')
        else:
            print(user_form.errors, profile_form.errors)
    else:
        if "code" in request.GET:
            code = request.GET["code"]
            token, refresh, expires_in = get_token(code)
            expires_at = datetime.datetime.now() + datetime.timedelta(seconds = expires_in)
            sp = spotipy.Spotify(auth = token)
            data = sp.me()
            spotify_user_id = data['id']
            display_name = data['display_name']
            try:
                archived_user = UserProfile.objects.get(spotify_user_id = spotify_user_id)
                return HttpResponseRedirect('/spotify_convert/login')
            except UserProfile.DoesNotExist as e:
                user_form = UserForm()
                profile_form = UserProfileForm(initial = {'spotify_token':token,
                                                          'spotify_refresh':refresh,
                                                          'spotify_user_id':spotify_user_id,
                                                          'spotify_expires_at': expires_at,
                                                          'display_name': display_name})
                context = {'user_form':user_form,'profile_form': profile_form, 'registered': registered}
        else:
            client_id = os.environ.get('SPOTIFY_CLIENT_ID')
            callback = helper.get_callback()
            spotify_url = "https://accounts.spotify.com/authorize?client_id=" + client_id + \
                            "&response_type=code&redirect_uri=" + \
                            callback + "&scope=user-library-modify+user-library-read"
            context = {'spotify_url':spotify_url}
    return render(request, 'spotify_convert/register.html', context)


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