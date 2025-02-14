import unittest
from main import sanitize_filename, check_track_exists, load_local_playlists

class TestMainFunctions(unittest.TestCase):

    def test_sanitize_filename(self):
        self.assertEqual(sanitize_filename('test/name'), 'testname')
        self.assertEqual(sanitize_filename('another:test'), 'anothertest')

    def test_check_track_exists(self):
        local_tracks = [
            {'name': 'Track 1', 'artist': 'Artist 1', 'duration_ms': 200000},
            {'name': 'Track 2', 'artist': 'Artist 2', 'duration_ms': 250000}
        ]
        spotify_track = {'name': 'Track 1', 'artist': 'Artist 1', 'duration_ms': 200000}
        self.assertTrue(check_track_exists(local_tracks, spotify_track))

        spotify_track = {'name': 'Track 3', 'artist': 'Artist 3', 'duration_ms': 300000}
        self.assertFalse(check_track_exists(local_tracks, spotify_track))

    def test_load_local_playlists(self):
        # Create a temporary JSON file for testing
        import json
        import tempfile

        test_data = {
            'playlist1': [
                {'name': 'Track 1', 'artist': 'Artist 1', 'duration_ms': 200000},
                {'name': 'Track 2', 'artist': 'Artist 2', 'duration_ms': 250000}
            ],
            'playlist2': [
                {'name': 'Track 3', 'artist': 'Artist 3', 'duration_ms': 300000}
            ]
        }

        with tempfile.NamedTemporaryFile('w', delete=False) as tmp_file:
            json.dump(test_data, tmp_file)
            tmp_file_path = tmp_file.name

        local_playlists = load_local_playlists(tmp_file_path)
        self.assertIsInstance(local_playlists, dict)
        self.assertIn('playlist1', local_playlists)
        self.assertIsInstance(local_playlists['playlist1'], list)

        # Clean up the temporary file
        import os
        os.remove(tmp_file_path)

if __name__ == '__main__':
    unittest.main()