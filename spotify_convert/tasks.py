from __future__ import absolute_import, unicode_literals
import spotipy
import xml.etree.ElementTree as ET
from Music.celery import app
import requests, os
import spotify_convert.helper as helper
import boto3
from spotify_convert.models import UserProfile, AddedSong, MissedSong
from pprint import pprint
from .models import User

@app.task
def go(library_url, user):
    sp = spotipy.Spotify(auth = user.userprofile.spotify_token)
    tree = load_tree(library_url)
    tracks = find_track_info(tree)
    success, fails, errors = match_apple_to_spotify(tracks, sp, user.userprofile)
    send_message("Completed moving songs!", "Moved: " + str(success) + ' songs and Missed: ' + str(fails) + ' songs. Totals Errors: ' + str(errors), user.userprofile.email, "Tune Transfer", 'tunes@mikevasiliou.com')
    return True


def authorize_spotify(code):
    token, refresh = get_token(code)
    sp = spotipy.Spotify(auth = token)
    return sp


def get_token(code):
    client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
    print(client_secret)
    callback = helper.get_callback()
    params = {'grant_type':'authorization_code', 'code':code, 'redirect_uri':callback}
    req = requests.post(
            'https://accounts.spotify.com/api/token',
            data = params,
            auth = (client_id, client_secret)
    )
    data = req.json()
    token = data['access_token']
    refresh = data['refresh_token']
    expires_in = data['expires_in']
    return token, refresh, expires_in


def load_tree(filekey):
    out_file = get_library_file(filekey)
    tree = ET.parse(out_file)
    root = tree.getroot()[0]
    tracks = root.find('dict').findall('dict')
    return tracks


def get_library_file(filekey):
    access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    session = boto3.Session(aws_access_key_id = access_key, aws_secret_access_key = secret_key)
    s3 = session.client('s3')
    bucket_name = "spotify-convert"
    key = filekey.split("/")[-1]
    out_file = "library.xml"
    s3.download_file(bucket_name, key, out_file)
    return out_file


def find_track_info(tracks):
    tracks_output = []
    for track in tracks:
        items = list(track)
        keys = track.findall('key')
        track_data = {}
        for i in range(len(keys)):
            track_data[keys[i].text] = items[i*2 + 1].text
        tracks_output.append(track_data)
    return tracks_output


def match_apple_to_spotify(tracks, sp, user):
    success = 0
    fails = 0
    errors = 0
    for song in tracks:
        success,fails,errors = match_song(sp, song, success, fails, errors, user)
    return success, fails, errors


def match_song(sp, song, success, fails, errors,user):
    if 'Artist' in song and 'Name' in song and 'Podcast' not in song:
        apple_name = song['Name']
        apple_artist = song['Artist']
        apple_id = song['Track ID']
        match_name = apple_name.lower()
        match_artist = apple_artist.lower()
        match_name_split = match_name.split('(')[0]
        try:
            results = sp.search(q = 'track:' + apple_name + ' artist:' + apple_artist, type = 'track')
            results = results['tracks']['items']

            for item in results:
                track_id = item['id']
                spotify_name = item['name']
                spot_name = spotify_name.lower()
                spot_artists = [artist['name'].lower() for artist in item['artists']]

                if (match_name == spot_name or
                    match_name in spot_name or
                    spot_name in match_name or
                    match_name_split in spot_name or
                    spot_name in match_name_split) and match_artist in spot_artists:

                    if add_track(sp, user, track_id, apple_name, apple_artist, apple_id, spotify_name):
                        success += 1
                    break
                if item == results[-1]:
                    fails += 1
                    no_match(user, apple_name, apple_artist, apple_id)
        except Exception as e:
            print(e, e.args)
            errors += 1
            no_match(user, apple_name, apple_artist, apple_id)
    return success, fails, errors


def add_track(sp,user, spotify_id, apple_name, apple_artist, apple_id, spotify_name):
    check = sp.current_user_saved_tracks_contains(tracks = [spotify_id])[0]
    if check:
        return False
    sp.current_user_saved_tracks_add(tracks = [spotify_id])
    added_song = AddedSong(spotify_user = user,
                            apple_name = apple_name,
                            apple_artist = apple_artist,
                            apple_id = apple_id,
                            spotify_name = spotify_name,
                            spotify_id = spotify_id)
    added_song.save()
    return True


def no_match(user, apple_name, apple_artist, apple_id):
    missed_song = MissedSong(spotify_user = user,
                              apple_name = apple_name,
                              apple_artist = apple_artist,
                              apple_id = apple_id)

    missed_song.save()

@app.task
def send_message(subject, message, recipients, sender_name, sender_email, attachments = [], cc = None,
                  bcc = None, deliverytime = None, campaign = None, tag = None, dkim = False, testmode = False,
                  tracking = True, tracking_opens = True, tracking_clicks = True, require_tls = False,
                  skip_verification = False):

    if type(attachments) is str:
        attachments = [attachments]

    files = []
    for file in attachments:
        files.append(("attachment", open(file)))

    if type(recipients) is str:
        recipients = [recipients]

    domain_name = "mikevasiliou.com"
    api_key = os.environ.get('MAILGUN_KEY')
    return requests.post(
            "https://api.mailgun.net/v3/" + domain_name + "/messages",
            auth = ("api", api_key),
            files = files,
            data = {"from":sender_name + " <" + sender_email + ">",
                    "to":recipients,
                    "cc":cc,
                    "bcc":bcc,
                    "subject":subject,
                    "html":message,
                    "o:campaign":campaign,
                    "o:tag":tag,
                    "o:dkim":dkim,
                    "o:deliverytime":deliverytime,
                    "o:testmode":testmode,
                    "o:tracking":tracking,
                    "o:tracking-opens":tracking_opens,
                    "o:tracking-clicks":tracking_clicks,
                    "o:require-tls":require_tls,
                    "o:skip_verification":skip_verification})