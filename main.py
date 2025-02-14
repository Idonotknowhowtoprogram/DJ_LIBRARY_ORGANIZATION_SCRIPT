import asyncio
import os
import re
import json
import logging
from spotify import get_spotify_playlists, get_playlist_tracks
from youtube_downloader import download_from_youtube
from local_playlists import save_local_playlist
from soundcloud_downloader import download_from_soundcloud

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', '', filename)

def check_track_exists(local_tracks, spotify_track):
    if not isinstance(local_tracks, list) or not isinstance(spotify_track, dict):
        logging.error("Invalid input types for check_track_exists")
        return False

    sanitized_spotify_track_name = sanitize_filename(spotify_track.get('name', '').strip().lower())
    sanitized_spotify_artist_name = sanitize_filename(spotify_track.get('artist', '').strip().lower())

    for local_track in local_tracks:
        if not isinstance(local_track, dict):
            logging.error("Invalid local_track type")
            continue

        if (sanitize_filename(local_track.get('name', '').strip().lower()) == sanitized_spotify_track_name and
            sanitize_filename(local_track.get('artist', '').strip().lower()) == sanitized_spotify_artist_name and
            local_track.get('duration_ms', 0) == spotify_track.get('duration_ms', 0)):
            return True
    return False

def write_results_to_file(results, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        for playlist_name, tracks in results.items():
            file.write(f"Playlist: {playlist_name}\n")
            for track, source in tracks:
                file.write(f"  Track: {track} (Downloaded from {source})\n")
            file.write("\n")

def load_local_playlists(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            local_playlists = json.load(file)
            if not isinstance(local_playlists, dict):
                raise ValueError("Invalid local playlists structure")
            for playlist_name, tracks in local_playlists.items():
                if not isinstance(tracks, list):
                    raise ValueError(f"Invalid tracks list for playlist {playlist_name}")
        for track in tracks:
                    if not isinstance(track, dict):
                        raise ValueError(f"Invalid track structure in playlist {playlist_name}")
        return local_playlists
    except Exception as e:
        logging.error(f"Error loading local playlists: {e}")
        return {}

async def main():
    local_playlists_file = 'local_playlists.json'
    local_playlists = load_local_playlists(local_playlists_file)
    spotify_playlists = get_spotify_playlists()

    print("Available Spotify playlists:")
    for idx, playlist in enumerate(spotify_playlists):
        print(f"{idx + 1}. {playlist['name']}")

    selected_indices = input("Enter the numbers of the playlists you want to sync (comma-separated): ")
    selected_indices = [int(idx.strip()) - 1 for idx in selected_indices.split(',')]

    results = {}

    for idx in selected_indices:
        playlist = spotify_playlists[idx]
        playlist_name = playlist['name']
        playlist_id = playlist['id']
        tracks = get_playlist_tracks(playlist_id)

        local_playlist_dir = os.path.join('C:\\Users\\liamp\\OneDrive\\Desktop\\mp3_library', playlist_name)
        if not os.path.exists(local_playlist_dir):
            os.makedirs(local_playlist_dir)
            logging.info(f"Created new local playlist directory: {local_playlist_dir}")

        update_dir = os.path.join(local_playlist_dir, 'update')
        if not os.path.exists(update_dir):
            os.makedirs(update_dir)
            logging.info(f"Created 'update' directory within {local_playlist_dir}")

        results[playlist_name] = []

        for track in tracks:
            track_name = track['track']['name']
            artist_name = track['track']['artists'][0]['name']
            spotify_track = {
                'name': track_name,
                'artist': artist_name,
                'duration_ms': track['track']['duration_ms']
            }

            if not check_track_exists(local_playlists.get(playlist_name, []), spotify_track):
                if download_from_youtube(track_name, artist_name, playlist_name, output_dir=update_dir, spotify_track=spotify_track):
                    results[playlist_name].append((track_name, 'YouTube'))
                else:
                    if await download_from_soundcloud(track_name, playlist_name, output_dir=update_dir):
                        results[playlist_name].append((track_name, 'Soundcloud'))

    write_results_to_file(results, 'download_results.txt')
    save_local_playlist(results, 'C:\\Users\\liamp\\OneDrive\\Desktop\\mp3_library')

if __name__ == '__main__':
    asyncio.run(main())