from __future__ import absolute_import, unicode_literals
import csv
import spotipy
import spotipy.util as util
import xml.etree.ElementTree as ET
from Music.celery import app
import requests, os
import spotify_convert.helper as helper
import boto3



@app.task
def go(library_url, code):
    sp_client_id = os.environ.get('CLIENT_ID')
    sp_client_secret = os.environ.get('CLIENT_SECRET')
    callback = helper.get_callback()
    token, refresh = get_token(code, callback, sp_client_id, sp_client_secret)

    tree = load_tree(library_url)
    tracks = find_track_info(tree)
    sp = spotipy.Spotify(auth = token)
    match_apple_to_spotify(tracks, sp)
    return True


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


def load_tree(filekey):
    access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

    session = boto3.Session(
            aws_access_key_id = access_key,
            aws_secret_access_key = secret_key,
    )

    #s3 = session.resource('s3')
    s3 = session.client('s3')
    bucket_name = "spotify-convert"
    key = filekey.split("/")[-1]
    out_file = "library.xml"
    print(key)
    s3.download_file(bucket_name, key, out_file)
    tree = ET.parse(out_file)
    root = tree.getroot()[0]
    tracks = root.find('dict').findall('dict')
    return tracks


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


def spotify_login():
    username = '12159028126'
    scope = 'user-library-read user-library-modify'
    token = util.prompt_for_user_token(username, scope)
    print(token)
    if token:
        sp = spotipy.Spotify(auth = token)
        return sp
    else:
        return None


def match_apple_to_spotify(tracks, sp):

    for song in tracks:
        if 'Artist' in song and 'Name' in song and 'Podcast' not in song:
            apple_name = song['Name']
            apple_artist = song['Artist']


            match_name = apple_name.lower()
            match_artist = apple_artist.lower()
            match_name_split = match_name.split('(')[0]
            try:
                results = sp.search(q = 'track:' + apple_name + ' ' + apple_name, type = 'track')
                results = results['tracks']['items']

                for item in results:

                    spot_name = item['name'].lower()
                    track_id = item['id']

                    spot_artists = [artist['name'].lower() for artist in item['artists']]

                    if (match_name == spot_name or
                        match_name in spot_name or
                        spot_name in match_name or
                        match_name_split in spot_name or
                        spot_name in match_name_split) and \
                        match_artist in spot_artists:

                        add_track(track_id, apple_name, apple_artist, sp)
                        break
                    if item == results[-1]:
                        no_match(apple_name, apple_artist, match_name, match_artist)
            except Exception as e:
                print(e, e.args)
                no_match(apple_name, apple_artist, match_name, match_artist)


def add_track(track_id, name, artist, sp):
    check = sp.current_user_saved_tracks_contains(tracks = [track_id])[0]
    if check:
        pass
    else:
        sp.current_user_saved_tracks_add(tracks = [track_id])
        print('Added track: ' + name.title() + ' by ' + artist.title())


def no_match(name, artist, match_name, match_artist):
    print('No Match for: ' + name + ' by ' + artist)
    print('Attempted to match with: ' + match_name + ' by ' + match_artist)
    #no_match_file = open('no_match.csv', 'a', newline = '')
    #no_match_writer = csv.writer(no_match_file)
    #no_match_writer.writerow([name, artist])