import boto3, os, datetime
from spotify_convert.models import AddedSong, MissedSong
from django.conf import settings
import xml.etree.ElementTree as ET
import spotify_convert.helper as helper
import spotipy
from django.utils import timezone


#Creates a list of all the tracks in an iTunes XML file
def load_tree(out_file):
    tree = ET.parse(out_file)
    root = tree.getroot()[0]
    tracks = root.find('dict').findall('dict')
    return tracks


#Grabs the XML file from our S3 Bucket
def get_library_file(filekey):
    access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    session = boto3.Session(aws_access_key_id = access_key, aws_secret_access_key = secret_key)
    s3 = session.client('s3')
    bucket_name = settings.S3_BUCKET
    key = filekey.split("/")[-1]
    out_file = "library.xml"
    s3.download_file(bucket_name, key, out_file)
    return out_file


#Outputs a list of dictionaries with track information
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

#Matchs each track to a spotify track and adds it
def match_apple_to_spotify(tracks, profile):
    #Ensures that token has not expired
    if timezone.now() >= profile.spotify_expires_at:
        helper.refresh_token(profile)
    sp = spotipy.Spotify(auth = profile.spotify_token)
        
    for song in tracks:
        try:
            match_song(sp, song, profile)
        except Exception as e:
            print(e, e.args)
            if timezone.now() >= profile.spotify_expires_at:
                helper.refresh_token(profile)
                sp = spotipy.Spotify(auth = profile.spotify_token)

#Uses name and artist to compare to a Spotify Search Query
def match_song(sp, song,user):
    if 'Artist' in song and 'Name' in song and 'Podcast' not in song:
        apple_name = song['Name']
        apple_artist = song['Artist']
        apple_id = song['Track ID']
        results = sp.search(q = 'track:' + apple_name + ' artist:' + apple_artist, type = 'track')
        results = results['tracks']['items']

        for item in results:
            track_id = item['id']
            if check_match(apple_name, apple_artist, item):
                add_track(sp, user, track_id, apple_name, apple_artist, apple_id)
                break
            if item == results[-1]:
                no_match(user, apple_name, apple_artist, apple_id)

#Confirms that a track matches a given Spotify track
def check_match(apple_name, apple_artist, item):
    spotify_name = item['name']
    spotify_artists = item['artists']
    match_name = apple_name.lower()
    match_artist = apple_artist.lower()
    match_name_split = match_name.split('(')[0]
    spot_name = spotify_name.lower()
    spot_artists = [artist['name'].lower() for artist in spotify_artists]
    return ((match_name == spot_name or
             match_name in spot_name or
             spot_name in match_name or
             match_name_split in spot_name or
             spot_name in match_name_split) and match_artist in spot_artists)

#Adds track to library if it is not already present
def add_track(sp,user, spotify_id, apple_name, apple_artist, apple_id):
    check = sp.current_user_saved_tracks_contains(tracks = [spotify_id])[0]
    if not check:
        sp.current_user_saved_tracks_add(tracks = [spotify_id])
        added_song = AddedSong(spotify_user = user,
                                apple_name = apple_name,
                                apple_artist = apple_artist,
                                apple_id = apple_id,
                                spotify_id = spotify_id)
        added_song.save()

#Catalogs missed tracks for later retrieval
def no_match(user, apple_name, apple_artist, apple_id):
    missed_song = MissedSong(spotify_user = user,
                              apple_name = apple_name,
                              apple_artist = apple_artist,
                              apple_id = apple_id)
    missed_song.save()