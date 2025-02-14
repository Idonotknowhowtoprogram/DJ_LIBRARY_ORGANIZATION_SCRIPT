# soundcloud_downloader.py
from sclib.asyncio import SoundcloudAPI, Track
import asyncio
import os
import re

def sanitize_search_query(query):
    # Remove problematic characters but preserve essential parts of the track name
    return re.sub(r'[\\/*?:"<>|]', '', query)

async def download_from_soundcloud(track_name, playlist_name, output_dir=None):
    if not track_name:
        print("Error: Track name is None or empty.")
        return False

    api = SoundcloudAPI()
    try:
        sanitized_track_name = sanitize_search_query(track_name)
        result = await api.resolve(f'https://soundcloud.com/search?q={sanitized_track_name}')
        if isinstance(result, Track):
            filename = os.path.join(output_dir, playlist_name, f'{result.artist} - {result.title}.mp3') if output_dir else f'{result.artist} - {result.title}.mp3'
            os.makedirs(os.path.join(output_dir, playlist_name), exist_ok=True)
            with open(filename, 'wb+') as file:
                await result.write_mp3_to(file)
            print(f"Downloaded {filename} from Soundcloud")
            return True
        else:
            print(f"Could not find track: {track_name} on Soundcloud")
            print(f"Result type: {type(result)}")
            print(f"Result content: {result}")
            return False
    except Exception as e:
        print(f"Error resolving track {track_name} on Soundcloud: {e}")
        return False