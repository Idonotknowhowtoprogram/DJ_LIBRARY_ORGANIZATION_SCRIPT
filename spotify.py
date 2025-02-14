# spotify.py

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                                                client_secret=SPOTIFY_CLIENT_SECRET,
                                                redirect_uri=SPOTIFY_REDIRECT_URI,
                                               scope="playlist-read-private"))
def get_spotify_playlists():
    try:
        playlists = sp.current_user_playlists()
        if not playlists['items']:
            print("No playlists found.")
            return []

        print(f"Fetched {len(playlists['items'])} playlists")
        for playlist in playlists['items']:
            print(f"Playlist: {playlist['name']} (ID: {playlist['id']})")
        return playlists['items']
    except Exception as e:
        print(f"Error fetching Spotify playlists: {e}")
        return []

def get_playlist_tracks(playlist_id):
    if not playlist_id:
        print("Error: Playlist ID is None or empty.")
        return []

    try:
        results = sp.playlist_items(playlist_id)
        if results is None:
            print(f"No results found for playlist {playlist_id}")
            return []

        tracks = results['items']
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])

        print(f"Fetched {len(tracks)} tracks for playlist {playlist_id}")
        for track in tracks:
            print(f"Track: {track['track']['name']} (ID: {track['track']['id']})")
        return tracks
    except Exception as e:
        print(f"Error fetching tracks for playlist {playlist_id}: {e}")
        return []