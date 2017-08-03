import requests

import constants


class Playlist:
    def __init__(self, internal_id, spotify_id, name, owner, track_count, track_url, public):
        self.internal_id = internal_id
        self.spotify_id = spotify_id
        self.name = name
        self.owner = owner
        self.track_count = track_count
        self.track_url = track_url
        self.public = public
        self.tracks = None

    def fetch_tracks(self, access_token):
        # Fetch tracks from spotify
        if self.tracks:
            return self.tracks
        self.tracks = []
        tracks_request_param = {"access_token": access_token}
        request_url = self.track_url
        while request_url:
            tracks_request = requests.get(request_url, params=tracks_request_param)
            playlists_data = tracks_request.json()
            self.tracks = self.tracks + playlists_data["items"]
            request_url = playlists_data["next"]
        return self.tracks
