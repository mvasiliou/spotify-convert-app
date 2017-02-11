from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UploadFileForm
from spotify_convert.tasks import go
import json, boto3, os
import spotify_convert.helper as helper
from django.conf import settings

# Create your views here.
def index(request):
    client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    print(client_id)
    callback = helper.get_callback()
    spotify_url = "https://accounts.spotify.com/authorize?client_id=" + client_id + \
                  "&response_type=code&redirect_uri=" + \
                  callback + "&scope=user-library-modify+user-library-read"
    context = {'spotify_url':spotify_url}

    if "code" in request.GET:
        code = request.GET["code"]
        file_form = UploadFileForm(initial = {'spotify_code':code})
        context['file_form'] = file_form
    return render(request, 'spotify_convert/index.html', context)


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
    if request.method == 'POST':
        form = UploadFileForm(request.POST)
        if form.is_valid():
            library_url = form.cleaned_data['file_url']
            spotify_code = form.cleaned_data['spotify_code']
            email = form.cleaned_data['email']
            go.delay(library_url, spotify_code, email)
            return HttpResponseRedirect('/spotify_convert/')
        else:
            print('Form is not valid')
            print(form.errors)
    else:
        form = UploadFileForm()
    return HttpResponseRedirect('/spotify_convert/')


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