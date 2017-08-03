import logging

import requests

import constants
from oauthtool import implicit_flow
from playlist import Playlist


def _authorize():
    # Start OAuth2 implicit flow
    auth_response = implicit_flow(constants.authorizeUrl, constants.clientId)

    # Check if authorization was successful
    if "error" in auth_response and auth_response["error"] is not None:
        logging.error("Authentication failed. Error message: {0}".format(auth_response["error_description"]))
        return False

    return auth_response["access_token"]


# Build an internal Playlist object from a Spotify playlist object
def _build_playlist(idx, plist):
    return Playlist(idx, plist["id"], plist["name"], plist["owner"]["id"], plist["tracks"]["total"],
                    plist["tracks"]["href"], plist["public"])


def _get_uri_set_from_ids(id_list):
    track_objects = []
    for bl in id_list:
        track_objects = track_objects + playlists[int(bl)].fetch_tracks(access_token)

    uris = set()
    for track in track_objects:
        uris.add(track["track"]["uri"])

    # delete local tracks from the set
    uris_no_local = set()
    for u in uris:
        if not u.startswith("spotify:local"):
            uris_no_local.add(u)
    return uris_no_local


access_token = _authorize()

# Fetch playlists from spotify
playlists_request_param = {"access_token": access_token,
                           "limit": 50}
playlists_request = requests.get(constants.spotifyBaseUrl + "/users/" + constants.spotifyUser + "/playlists",
                                 params=playlists_request_param)
playlists_data = playlists_request.json()

# Copy playlist data into internal object list
playlists = []
# TODO: Add support for more than 50 playlists
for i in range(0, len(playlists_data["items"]) - 1):
    playlists.append(_build_playlist(i, playlists_data["items"][i]))

# Print fetched playlists
print("Your playlists are listed below")
for p in playlists:
    print("[" + str(p.internal_id) + "] " + p.name)

# Create new playlist
playlist_name = input("Enter a name for your new playlist: ")

create_request_data = {"name": playlist_name,
                       "public": "false"}
create_request_param = {"access_token": access_token,
                        "content_type": "application/json"}
create_request = requests.post(constants.spotifyBaseUrl + "/users/" + constants.spotifyUser + "/playlists",
                               params=create_request_param, json=create_request_data)

if create_request.status_code is not 201:
    print("An error occurred while creating the new playlist, status code: " + str(create_request.status_code))
    exit(1)
new_playlist_id = create_request.json()["id"]

base_lists = input("Type a comma seperated list of the playlist id's you want to use tracks from: ")
base_lists = base_lists.split(",")
base_uris = _get_uri_set_from_ids(base_lists)

remove_lists = input("Type a comma seperated list of the playlist id's you don't want any trakcks of: ")
remove_lists = remove_lists.split(",")
remove_uris = _get_uri_set_from_ids(remove_lists)

base_uris = base_uris - remove_uris

uri_list = list(base_uris)

insert_request_param = {"access_token": access_token,
                        "content_type": "application/json"}
start = 0
while start < len(uri_list):
    insert_request = requests.post(constants.spotifyBaseUrl + "/users/" + constants.spotifyUser + "/playlists/" +
                                   new_playlist_id + "/tracks",
                                   params=insert_request_param, json=uri_list[start:start + 100])
    if insert_request.status_code is not 201:
        print(
            "An error occurred while inserting tracks into the new playlist, status code: " + str(insert_request.status_code))
        exit(1)
    start = start + 100

print("Successfully created new playlist!")
