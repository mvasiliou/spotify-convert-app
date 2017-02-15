from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UploadFileForm
from spotify_convert.tasks import go
import spotify_convert.helper as helper
import os


def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/spotify_convert/convert/')
    else:
        spotify_url = helper.generate_spotify_url()
        context = {'spotify_url':spotify_url}
        return render(request, 'spotify_convert/index.html', context)


def convert(request):
    if request.user.is_authenticated():
        file_form = UploadFileForm()
        context = {'file_form': file_form}
        return render(request, 'spotify_convert/convert.html', context)
    return HttpResponseRedirect('/spotify_convert/register/')


def complete(request):
    if request.user.is_authenticated():
        user = request.user
        added_songs = user.userprofile.addedsong_set.all()
        missed_songs = user.userprofile.missedsong_set.all()
        return render(request,'spotify_convert/complete.html',{'added_songs':added_songs, 'missed_songs':missed_songs})
    return HttpResponseRedirect('/spotify_convert/register/')


def sign_s3(request):
    s3_bucket = os.environ.get('S3_BUCKET_NAME')
    file_name = request.GET['file_name']
    file_type = request.GET['file_type']
    json_output = helper.get_pre_signed_post(s3_bucket, file_name, file_type)
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
    return HttpResponseRedirect('/spotify_convert/convert/')
        

def register(request):
    if request.method == 'POST':
        return helper.new_user(request)
    if "code" in request.GET:
        return helper.setup_reg_forms(request)
    spotify_url =helper.generate_spotify_url()
    context = {'spotify_url':spotify_url}
    return render(request, 'spotify_convert/register.html', context)


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username = username, password = password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/spotify_convert/convert/')
            else:
                return HttpResponse("Your Tune Transfer account is disabled")
        else:
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login credentials.")
    else:
        return render(request, 'spotify_convert/login.html')

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/spotify_convert/')