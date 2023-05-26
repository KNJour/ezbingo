import requests
from mysqlconnection import connectToMySQL
client_id = "01ccc9daf43d4fc2b7989fc9bf411861"
client_secret = "5d76f7c1a9cb4534bf08f7b24a8f0da7"

test_urls = [
    "https://open.spotify.com/track/4lc26OWTRFdEZediB0picq",
    "https://open.spotify.com/track/41olw7iIGVyds8dnSR9pb0",
    "https://open.spotify.com/track/3L7RFZ8KMWZCM2AHXdpjeh",
    "https://open.spotify.com/track/1NMkU6FkMKGjdz1u5krIfX"
]

def get_access_token(client_id, client_secret):
    url = "https://accounts.spotify.com/api/token"
    auth_data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    auth_response = requests.post(url, data=auth_data)
    access_token = auth_response.json().get("access_token")
    return access_token

def get_track_info(track_id, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    track_url = f"https://api.spotify.com/v1/tracks/{track_id}"
    track_response = requests.get(track_url, headers=headers)
    track_data = track_response.json()
    track_title = track_data["name"]
    artist_name = track_data["artists"][0]["name"]
    return track_title, artist_name

access_token = get_access_token(client_id, client_secret)

def convert_to_playlist(url_list, user_id, playlist_name):
    playlist_data = {
            "name" : playlist_name,
            "user_id" : user_id
        }
        # Creates a playlist with the playlist_name variable for the name
    playlist_query = "INSERT INTO playlists (user_id, playlist_name, created_at, updated_at) VALUES (%(user_id)s, %(name)s, NOW(),NOW())"
    newPlaylist = connectToMySQL('ezbingo').query_db(playlist_query,playlist_data)
        # Retrieves the ID of the playlist created to insert songs into from the list of url's
    playlist_id_query = "SELECT id FROM Playlists WHERE playlists.user_id = %(user_id)s ORDER BY id DESC LIMIT 1"
    playlist_id = connectToMySQL('ezbingo').query_db(playlist_id_query, playlist_data)
    print(playlist_id)
    # Loops through list of addresses, 
    # print("test type:")
    # print(playlist_id)
    # print(type(playlist_id[0]['id']))
    for url in url_list:
        track_id = url.split('/')[-1]
        song_title, artist_name = get_track_info(track_id, access_token)
        print(type(song_title))
        data = {
            "title" : song_title,
            "artist" : artist_name,
            "playlist_id" : int(playlist_id[0]['id']),
         }
        query = "INSERT INTO songs (playlist_id, title, artist, created_at, updated_at) VALUES (%(playlist_id)s, %(title)s, %(artist)s, NOW(),NOW())"
        addSong = connectToMySQL('ezbingo').query_db(query,data)

