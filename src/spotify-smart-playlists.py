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
        if (track["track"] != None):
            uris.add(track["track"]["uri"])

    # delete local tracks from the set
    uris_no_local = set()
    for u in uris:
        if not u.startswith("spotify:local"):
            uris_no_local.add(u)
    return uris_no_local


def _fetch_playlists():
    # Fetch playlists from spotify
    plists = []
    playlists_request_param = {"access_token": access_token,
                               "limit": 50}
    request_url = constants.spotifyBaseUrl + "/users/" + constants.spotifyUser + "/playlists"

    idx = 0
    while request_url:
        playlists_request = requests.get(request_url, params=playlists_request_param)
        playlists_data = playlists_request.json()

        # Copy playlist data into internal object list
        for i in range(0, len(playlists_data["items"])):
            plists.append(_build_playlist(idx, playlists_data["items"][i]))
            idx += 1

        request_url = playlists_data["next"]

    return plists


def _filter_tracks(base, remove):
    base = base - remove

    return list(base)


def _generate_playlist(name, tracks):
    create_request_data = {"name": name,
                           "public": "false"}
    create_request_param = {"access_token": access_token,
                            "content_type": "application/json"}
    create_request = requests.post(constants.spotifyBaseUrl + "/users/" + constants.spotifyUser + "/playlists",
                                   params=create_request_param, json=create_request_data)

    if create_request.status_code is not 201:
        print("An error occurred while creating the new playlist, status code: " + str(create_request.status_code))
        exit(1)
    new_playlist_id = create_request.json()["id"]

    insert_request_param = {"access_token": access_token,
                            "content_type": "application/json"}
    start = 0
    while start < len(tracks):
        insert_request = requests.post(
            constants.spotifyBaseUrl + "/users/" + constants.spotifyUser + "/playlists/" +
            new_playlist_id + "/tracks",
            params=insert_request_param, json=tracks[start:start + 100])
        if insert_request.status_code is not 201:
            print(
                "An error occurred while inserting tracks into the new playlist, status code: " + str(
                    insert_request.status_code))
            exit(1)
        start = start + 100

    print("Successfully created new playlist!")


access_token = _authorize()

playlists = _fetch_playlists()
base_uris = set()
remove_uris = set()

while 1:
    print("### Menu ###")
    print("[1] Print list of available playlists")
    print("[2] Refresh list of playlists")
    print("[3] Specify base playlists")
    print("[4] Specify playlists to exclude tracks from")
    print("[5] Generate new playlist")
    print("[6] Exit")
    selection = input("Choose one of the options listed above: ")
    if selection == "1":
        print("Your playlists are listed below")
        for p in playlists:
            print("[" + str(p.internal_id) + "] " + p.name)
    elif selection == "2":
        playlists = _fetch_playlists()
    elif selection == "3":
        base_lists = input("Type a comma seperated list of the playlist id's you want to use tracks from: ")
        base_lists = base_lists.split(",")
        base_uris = _get_uri_set_from_ids(base_lists)
    elif selection == "4":
        remove_lists = input("Type a comma seperated list of the playlist id's you don't want any trakcks of: ")
        remove_lists = remove_lists.split(",")
        remove_uris = _get_uri_set_from_ids(remove_lists)
    elif selection == "5":
        playlist_name = input("Enter a name for your new playlist: ")
        result_tracks = _filter_tracks(base_uris, remove_uris)
        _generate_playlist(playlist_name, result_tracks)
    elif selection == "6":
        break
    else:
        print("Please select one of the listed options")
