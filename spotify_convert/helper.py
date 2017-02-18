from django.conf import settings
import boto3, json, spotipy
from .models import UserProfile
from .forms import UserProfileForm, UserForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login
import os, requests, datetime
from django.utils import timezone


#Generates signed POST to our S3 bucket
def get_pre_signed_post(s3_bucket, file_name, file_type):
    s3 = boto3.client('s3')
    presigned_post = s3.generate_presigned_post(
        Bucket = s3_bucket,
        Key = file_name,
        Fields = {"acl": "private", "Content-Type": file_type},
        Conditions = [
            {"acl": "private"},
            {"Content-Type": file_type}
        ],
        ExpiresIn = 3600
    )
    json_output = json.dumps({'data': presigned_post,
                              'url': 'https://%s.s3.amazonaws.com/%s' % (s3_bucket, file_name)
                            })
    return json_output


#Sets up the registration form based on authorization info from Spotify
def setup_reg_forms(request):
    code = request.GET["code"]
    token, refresh, expires_at = get_token(code)
    
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
        context = {'user_form':user_form,'profile_form': profile_form}
        return render(request, 'spotify_convert/register.html', context)


#Requests a Token from the Spotify Token Endpoint
def get_token(code, refresh = False):
    client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
    callback = settings.SPOTIFY_CALLBACK
    params = {'grant_type':'authorization_code', 'code':code, 'redirect_uri':callback}
    if refresh:
        params = {'grant_type':'refresh_token', 'refresh_token':code, 'redirect_uri':callback}
    req = requests.post(
            'https://accounts.spotify.com/api/token',
            data = params,
            auth = (client_id, client_secret)
    )
    data = req.json()
    token = data['access_token']
    expires_in = data['expires_in']
    expires_at = timezone.now() + datetime.timedelta(seconds = expires_in)
    
    if refresh:
        return token, expires_at

    refresh = data['refresh_token']
    return token, refresh, expires_at

#Uses the token API endpoint to refresh an expired token and save to UserProfile
def refresh_token(profile):
    token, expires_at = get_token(profile.spotify_refresh, True)
    profile.spotify_token = token
    profile.spotify_expires_at = expires_at
    profile.save()


#Creates a new user based on the UserForm and UserProfileForm. Logs the user in.
def new_user(request):
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
        user = authenticate(username = username, password = password)
        if user:
            login(request, user)
            return HttpResponseRedirect('/spotify_convert/convert/')
        else:
            #Send to a login page if it didn't work later 
            return HttpResponseRedirect('/spotify_convert/login/')
    else:
        print(user_form.errors, profile_form.errors)
        return render(request, 'spotify_convert/register.html', {})


#Authorizes a Spotipy object given an auth code
def authorize_spotify(code):
    token, refresh = get_token(code)
    sp = spotipy.Spotify(auth = token)
    return sp

#Uses our callback setting to generate the Spotify auth URL
def generate_spotify_url():
    client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    callback = settings.SPOTIFY_CALLBACK
    spotify_url = "https://accounts.spotify.com/authorize?client_id=" + client_id + \
                  "&response_type=code&redirect_uri=" + \
                  callback + "&scope=user-library-modify+user-library-read"
    return spotify_url