import logging
import requests

from oauthtool import implicit_flow

tokenUrl = "https://accounts.spotify.com/api/token"
authorizeUrl = "https://accounts.spotify.com/authorize"
clientId = "your_client_id_here"
clientSecret = "your_client_secret_here"
spotifyBaseUrl = "https://api.spotify.com/v1"

def _authorize():
    # Start OAuth2 implicit flow
    auth_response = implicit_flow(authorizeUrl, clientId)

    # Check if authorization was successful
    if "error" in auth_response and auth_response["error"] is not None:
        logging.error("Authentication failed. Error message: {0}".format(auth_response["error_description"]))
        return False

    return auth_response["access_token"]

access_token = _authorize()
p = {"access_token":access_token}
r = requests.get(spotifyBaseUrl + "/users/anabta/playlists", params=p)
print(r.text)
