import json
import logging
import constants

import requests

from oauthtool import implicit_flow

def _authorize():
    # Start OAuth2 implicit flow
    auth_response = implicit_flow(constants.authorizeUrl, constants.clientId)

    # Check if authorization was successful
    if "error" in auth_response and auth_response["error"] is not None:
        logging.error("Authentication failed. Error message: {0}".format(auth_response["error_description"]))
        return False

    return auth_response["access_token"]


access_token = _authorize()

token_param = {"access_token": access_token}

playlists_request = requests.get(constants.spotifyBaseUrl + "/users/anabta/playlists", params=token_param)
data = json.loads(playlists_request.text)

list_track_dict = {}

for i in range(0, data["total"] - 1):
    list_track_dict[data["items"][i]["name"]] = data["items"][i]["tracks"]["href"]

print("Your playlists are listed below")
keys_string = str(list_track_dict.keys())
pretty_keys_string = keys_string.replace("dict_keys(['", "").replace("'])", "").replace("', '", "\n")
print(pretty_keys_string)
correct_input = 0
while not correct_input:
    correct_input = 1
    user_input = input("Type a comma seperated list of the playlists you want to include into generation: ").split(",")
    for list in user_input:
        if list not in list_track_dict.keys():
            print("At least one of your specified lists could not be found on Spotify, please try again.")
            correct_input = 0
print(user_input)
