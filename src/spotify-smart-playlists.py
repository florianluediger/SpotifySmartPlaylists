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
token_param = {"access_token": access_token}

playlists_request = requests.get(constants.spotifyBaseUrl + "/users/" + constants.spotifyUser + "/playlists",
                                 params=token_param)
data = json.loads(playlists_request.text)

# Copy playlist data into internal object list
playlists = []
for i in range(0, data["total"] - 1):
    playlists.append(_build_playlist(i, data["items"][i]))

print("Your playlists are listed below")
for p in playlists:
    print("[" + str(p.internal_id) + "] " + p.name)

user_input = -1
while user_input not in range(0, len(playlists)):
    user_input = input("Type the id of one of the playlists above for testing purposes: ")
    user_input = 0 if user_input is "" else int(user_input)

print(playlists[user_input].name)
