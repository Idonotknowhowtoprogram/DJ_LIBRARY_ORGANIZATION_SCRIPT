# youtube_downloader.py

import yt_dlp
import os
import re

def sanitize_search_query(query):
    # Remove problematic characters but preserve essential parts of the track name
    return re.sub(r'[\\/*?:"<>|]', '', query)

def check_track_details(track_name, artist_name, spotify_track):
    sanitized_track_name = sanitize_search_query(track_name)
    sanitized_artist_name = sanitize_search_query(artist_name)
    sanitized_spotify_track_name = sanitize_search_query(spotify_track['name'])
    sanitized_spotify_artist_name = sanitize_search_query(spotify_track['artist'])

    return (sanitized_track_name == sanitized_spotify_track_name and
            sanitized_artist_name == sanitized_spotify_artist_name)

def download_from_youtube(track_name, artist_name, playlist_name, output_dir=None, spotify_track=None):
    if not track_name or not artist_name:
        print("Error: Track name or artist name is None or empty.")
        return False

    search_query = f"{track_name} {artist_name}"
    sanitized_search_query = sanitize_search_query(search_query)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_dir, playlist_name, f'{artist_name} - {track_name}.%(ext)s') if output_dir else f'{artist_name} - {track_name}.%(ext)s',
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(f"ytsearch:{sanitized_search_query}", download=False)
            if 'entries' in info_dict:
                video = info_dict['entries'][0]
                if check_track_details(track_name, artist_name, spotify_track):
                    ydl.download([video['webpage_url']])
                    print(f"Downloaded {track_name} by {artist_name} from YouTube")
                    return True
                else:
                    print(f"Track details do not match Spotify track: {track_name} by {artist_name}")
                    return False
            else:
                print(f"Could not find track: {track_name} by {artist_name} on YouTube")
                return False
        except Exception as e:
            print(f"Error downloading track {track_name} by {artist_name} from YouTube: {e}")
            return False