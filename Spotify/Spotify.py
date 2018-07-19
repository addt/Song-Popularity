#TODO 1. Structure according to classifier feed, 2. Get top 100 track ids

import requests
from requests.auth import HTTPBasicAuth
import sys
import csv

CLIENT_ID = "XXXXXXXXXXXXXXXXXXXX"
CLIENT_SECRET_ID = "XXXXXXXXXXXXXXXX"
AUTH_URL = "https://accounts.spotify.com/api/token?grant_type=client_credentials"
AUTH_TOKEN = None
CONTENT_TYPE = "application/x-www-form-urlencoded"
ACCEPT = "application/json"
HEADERS = {"content-type":CONTENT_TYPE, "Accept": ACCEPT}

TRACK_URL = "https://api.spotify.com/v1/tracks/"
AUDIO_FEATURE_URL = "https://api.spotify.com/v1/audio-features/"
fieldnames = ['artist_name','album_name', 'duration', 'track_popularity',
                      'track_name', 'danceability', 'energy',
                      'key', 'loudness', 'mode', 'speechiness',
                      'acousticness', 'instrumentalness', 'liveness',
                      'valence', 'tempo', 'artist_followers',
              'genres', 'artist_popularity', 'artist_top_tracks',
              'artist_album_count', 'album_popularity', 'release_date']

track_features = {}

def login_spotify():
    global AUTH_TOKEN
    print("Fetching the authentication token for the application")
    response = requests.post(AUTH_URL,
                            auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET_ID),
                                               headers=HEADERS)

    if (response.status_code != 200):
        print("ERROR: Unable to get authentication token. Response code is {}".format(response.status_code))
        print(response.json())
        sys.exit(0)

    AUTH_TOKEN = response.json()['access_token']
    print("Authentication token fetched successfully \n")

def track_level_features(track_id):
    global track_features
    track = track_id[0]
    if (len(track) == 0):
        return

    print("Fetching track level features for track with id {}".format(track))
    authorization = " ".join(("Bearer", AUTH_TOKEN))
    url = "".join((TRACK_URL, track))
    headers = {"Authorization": authorization}
    feature_map = {}
    try:
        response = requests.get(url, headers=headers)

        if (response.status_code != 200):
            print("ERROR: Unable to get track level features for track with id {}".format(track))
            print(response.json())
            return

        feature_map["album_name"] =response.json()['album']['name']
        feature_map["duration"] = response.json()['duration_ms']
        feature_map["track_popularity"] = response.json()['popularity']
        feature_map["track_name"] = response.json()['name']
        feature_map["artist_name"] = response.json()['artists'][0]['name']

        # To be popped later
        feature_map["artist_href"] = response.json()['artists'][0]['href']
        feature_map["album_href"] = response.json()['album']['href']

        track_features[track] = feature_map
    except Exception as e:
        print("ERROR: Unexpected error encountered: {}".format(e))
        raise
    else:
        print("Finished track level features for track with id {}".format(track))

def audio_features(track_id):
    global track_features
    track = track_id[0]
    if (len(track) == 0):
        return

    print("Fetching Audio features for track with id {}".format(track))
    authorization = " ".join(("Bearer", AUTH_TOKEN))
    url = "".join((AUDIO_FEATURE_URL, track))
    headers = {"Authorization": authorization}
    feature_map = track_features.get(track, {})
    try:
        response = requests.get(url, headers=headers)

        if (response.status_code != 200):
            print("ERROR: Unable to get audio features for track with id {}".format(track))
            print(response.json())
            return

        feature_map["danceability"] = response.json()['danceability']
        feature_map["energy"] = response.json()['energy']
        feature_map["key"] = response.json()['key']
        feature_map["loudness"] = response.json()['loudness']
        feature_map["mode"] = response.json()['mode']
        feature_map["speechiness"] = response.json()['speechiness']
        feature_map["acousticness"] = response.json()['acousticness']
        feature_map["instrumentalness"] = response.json()['instrumentalness']
        feature_map["liveness"] = response.json()['liveness']
        feature_map["valence"] = response.json()['valence']
        feature_map["tempo"] = response.json()['tempo']
        track_features[track] = feature_map
    except Exception as e:
        print("ERROR: Unexpected error encountered: {}".format(e))
        raise
    else:
        print("Finished Audio level features for track with id {}".format(track))

def audio_analysis(track_id):
    # Lets see if this one is needed
    pass

def album_features(track_id):
    global track_features
    track = track_id[0]
    if (len(track) == 0):
        return
    feature_map = track_features.get(track, None)

    if (feature_map == None):
        return

    album_url = feature_map["album_href"]

    authorization = " ".join(("Bearer", AUTH_TOKEN))
    headers = {"Authorization": authorization}
    payload = {'market': 'US'}

    try:
        response = requests.get(album_url, headers=headers, params=payload)

        if (response.status_code != 200):
            print("ERROR: Unable to get album for track with id {} \n".format(track))
            print(response.json())
            return

        feature_map["album_popularity"] = response.json()['popularity']
        feature_map["release_date"] = response.json()["release_date"]

        track_features[track] = feature_map
    except Exception as e:
        print("ERROR: Unexpected error encountered: {}".format(e))
        raise
    else:
        print("Finished album details for track with id {} \n".format(track))


def artist_features(track_id):
    global track_features
    track = track_id[0]
    if (len(track) == 0):
        return
    feature_map = track_features.get(track, None)

    if (feature_map == None):
        return

    artist_url = feature_map["artist_href"]

    authorization = " ".join(("Bearer", AUTH_TOKEN))
    headers = {"Authorization": authorization}

    try:
        response = requests.get(artist_url, headers=headers)

        if (response.status_code != 200):
            print("ERROR: Unable to get artist features for track with id {}".format(track))
            print(response.json())
            return

        feature_map["artist_followers"] =response.json()['followers']['total']
        feature_map["genres"] = response.json()['genres']
        feature_map["artist_popularity"] = response.json()['popularity']

        track_features[track] = feature_map
    except Exception as e:
        print("ERROR: Unexpected error encountered: {}".format(e))
        raise
    else:
        print("Finished artist level features for track with id {}".format(track))

def getAlbumTracksforArtist(track_id):
    global track_features
    track = track_id[0]
    if (len(track) == 0):
        return
    feature_map = track_features.get(track, None)

    if (feature_map == None):
        return

    artist_url = feature_map["artist_href"]

    authorization = " ".join(("Bearer", AUTH_TOKEN))
    headers = {"Authorization": authorization}
    artist_url = "".join((artist_url, "/top-tracks"))
    payload = {'country': 'US'}

    try:
        response = requests.get(artist_url, headers=headers, params=payload)

        if (response.status_code != 200):
            print("ERROR: Unable to get album features for track with id {} \n".format(track))
            print(response.json())
            return

        feature_map["artist_top_tracks"] = len(response.json()['tracks'])
    except Exception as e:
        print("ERROR: Unexpected error encountered: {}".format(e))
        raise

    artist_url = feature_map["artist_href"]

    authorization = " ".join(("Bearer", AUTH_TOKEN))
    headers = {"Authorization": authorization}
    artist_url = "".join((artist_url, "/albums"))
    payload = {'album_type': 'album', 'market': 'US'}

    try:
        response = requests.get(artist_url, headers=headers, params=payload)

        if (response.status_code != 200):
            print("ERROR: Unable to get album/track for track with id {} \n".format(track))
            print(response.json())
            return

        feature_map["artist_album_count"] = len(response.json()['items'])

        track_features[track] = feature_map
    except Exception as e:
        print("ERROR: Unexpected error encountered: {}".format(e))
        raise
    else:
        print("Finished album and track details for track with id {}".format(track))

def write_to_csv():
    global track_features
    global fieldnames

    with open('features.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for key in track_features:
            features = track_features[key]
            #Pop unnneded values from the dictionary
            features.pop("artist_href", None)
            features.pop("album_href", None)

            writer.writerow(features)

def main():
    # Login using client credentials and get the authentication token
    login_spotify()

    try:
        with open('tracks.csv') as csvDataFile:
            csvReader = csv.reader(csvDataFile)
            for row in csvReader:
                # Get track level features for all tracks in csv
                track_level_features(row)

                #Audio features for the track
                audio_features(row)

                #Artis details for the track
                artist_features(row)
                getAlbumTracksforArtist(row)

                #Album details for the tracks
                album_features(row)
    except FileNotFoundError as e:
        print("ERROR: Tracks csv doesn not exist or is in some other folder")
    except Exception as error:
        #print("Unexpected error: {}".format(error))
        raise
    else:
        print("Finished parsing all tracks")

    write_to_csv()

if __name__ == '__main__':
    main()
