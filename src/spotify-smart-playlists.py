import json
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
    print("An error occurred while creating the new playlist, status code: " + create_request.status_code)
    exit(1)
create_data = create_request.json()

user_input = -1
while user_input not in range(0, len(playlists)):
    user_input = input("Type the id of one of the playlists above for testing purposes: ")
    user_input = 0 if user_input is "" else int(user_input)

print(playlists[user_input].name)
