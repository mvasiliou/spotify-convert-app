from __future__ import absolute_import, unicode_literals
import csv
import spotipy
import spotipy.util as util
import xml.etree.ElementTree as ET
from Music.celery import app
from django.core.files.storage import FileSystemStorage
from django.conf import settings


@app.task
def go(path, token):
    #fs = FileSystemStorage()
    #file = fs.open(settings.BASE_DIR + path)
    #tree = load_tree(file)
    #tracks = find_track_info(tree)
    sp = spotipy.Spotify(auth = token)
    #match_apple_to_spotify(tracks, sp)


def load_tree(path):
    tree = ET.parse(path)
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


def print_spotify_tracks():
    results = sp.current_user_saved_tracks()
    for item in results['items']:
        track = item['track']
        print(track['name'] + ' - ' + track['artists'][0]['name'])


def match_apple_to_spotify(tracks, sp):
    spotify = spotipy.Spotify()

    for song in tracks:
        if 'Artist' and 'Name' in song:
            apple_name = song['Name'].lower()
            apple_artist = song['Artist'].lower()

        results = spotify.search(q = 'track:' + apple_name + ' ' + apple_artist, type = 'track')
        results = results['tracks']['items']

        for item in results:

            spot_name = item['name'].lower()
            track_id = item['id']

            spot_artists = [artist['name'].lower() for artist in item['artists']]

            if (
                        apple_name == spot_name or apple_name in spot_name or spot_name in apple_name) and \
                            apple_artist in spot_artists:
                add_track(track_id, apple_name, apple_artist, sp)
                break
            if item == results[-1]:
                no_match(apple_name, apple_artist)


def add_track(track_id, name, artist, sp):
    check = sp.current_user_saved_tracks_contains(tracks = [track_id])[0]
    if not check:
        sp.current_user_saved_tracks_add(tracks = [track_id])
        print('Added track ' + name.title() + ' by ' + artist.title())


def no_match(name, artist):
    no_match_file = open('no_match.csv', 'a', newline = '')
    no_match_writer = csv.writer(no_match_file)
    no_match_writer.writerow([name, artist])