import asyncio
import os
import re
from spotify import get_spotify_playlists, get_playlist_tracks
from youtube_downloader import download_from_youtube
from local_playlists import load_local_playlists, save_local_playlist
from soundcloud_downloader import download_from_soundcloud

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', '', filename)

def check_track_exists(local_tracks, spotify_track):
    sanitized_spotify_track_name = sanitize_filename(spotify_track['name'])
    sanitized_spotify_artist_name = sanitize_filename(spotify_track['artist'])
    for local_track in local_tracks:
        if (sanitize_filename(local_track['name']) == sanitized_spotify_track_name and
            sanitize_filename(local_track['artist']) == sanitized_spotify_artist_name and
            local_track['duration_ms'] == spotify_track['duration_ms']):
            return True
    return False

def write_results_to_file(results, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        for playlist_name, tracks in results.items():
            file.write(f"Playlist: {playlist_name}\n")
            for track, source in tracks:
                file.write(f"  Track: {track} (Downloaded from {source})\n")
            file.write("\n")

async def main():
    local_playlists_dir = 'C:\\Users\\liamp\\OneDrive\\Desktop\\mp3_library'
    local_playlists = load_local_playlists(local_playlists_dir)
    spotify_playlists = get_spotify_playlists()

    # Display available Spotify playlists
    print("Available Spotify playlists:")
    for idx, playlist in enumerate(spotify_playlists):
        print(f"{idx + 1}. {playlist['name']}")

    # Prompt user to select playlists
    selected_indices = input("Enter the numbers of the playlists you want to sync (comma-separated): ")
    selected_indices = [int(idx.strip()) - 1 for idx in selected_indices.split(',')]

    results = {}

    for idx in selected_indices:
        playlist = spotify_playlists[idx]
        playlist_name = playlist['name']
        playlist_id = playlist['id']
        tracks = get_playlist_tracks(playlist_id)

        local_playlist_dir = os.path.join(local_playlists_dir, playlist_name)
        if not os.path.exists(local_playlist_dir):
            os.makedirs(local_playlist_dir)
            print(f"Created new local playlist directory: {local_playlist_dir}")

        update_dir = os.path.join(local_playlist_dir, 'update')
        if not os.path.exists(update_dir):
            os.makedirs(update_dir)
            print(f"Created 'update' directory within {local_playlist_dir}")

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
    save_local_playlist(results, local_playlists_dir)

if __name__ == '__main__':
    asyncio.run(main())