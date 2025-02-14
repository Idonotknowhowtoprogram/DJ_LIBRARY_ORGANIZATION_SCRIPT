# local_playlists.py
import os

def load_local_playlists(directory):
    playlists = {}
    for root, dirs, files in os.walk(directory):
        for dir_name in dirs:
            playlist_name = dir_name
            playlist_dir = os.path.join(root, dir_name)
            if playlist_name not in playlists:
                playlists[playlist_name] = []
            for file in os.listdir(playlist_dir):
                if file.endswith('.mp3'):
                    track_name = os.path.splitext(file)[0]
                    playlists[playlist_name].append(track_name)
    print(f"Loaded local playlists: {list(playlists.keys())}")
    return playlists

def save_local_playlist(playlists, directory):
    for playlist_name, tracks in playlists.items():
        playlist_dir = os.path.join(directory, playlist_name)
        os.makedirs(playlist_dir, exist_ok=True)
        for track in tracks:
            track_file = os.path.join(playlist_dir, f"{track}.mp3")
            if not os.path.exists(track_file):
                with open(track_file, 'wb') as file:
                    pass  # Create an empty file for the track