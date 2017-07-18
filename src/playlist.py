class Playlist:
    def __init__(self, internal_id, spotify_id, name, owner, track_count, track_url, public):
        self.internal_id = internal_id
        self.spotify_id = spotify_id
        self.name = name
        self.owner = owner
        self.track_count = track_count
        self.track_url = track_url
        self.public = public
