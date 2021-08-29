import os
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()
BILLBOARD_URL = os.environ['BILLBOARD_URL']
SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
REDIRECT_URI = os.environ['REDIRECT_URI']

# Spotify Authentication
sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope="playlist-modify-private",
            redirect_uri=REDIRECT_URI,
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            show_dialog=True,
            cache_path="token.txt"
        )
)

# Scraping Billboard 100
date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")

response = requests.get(f'{BILLBOARD_URL}{date}')
billboard_html = response.text

soup = BeautifulSoup(billboard_html, 'html.parser')
song_names_spans = soup.find_all('span', class_='chart-element__information__song text--truncate color--primary')
songs = [song.get_text() for song in song_names_spans]

# Searching Spotify for songs by title
year = date[:4]
track_uris = []
for song in songs:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    try:
        track_uri = result['tracks']['items'][0]['uri']
        track_uris.append(track_uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

# Creating a new private playlist in Spotify
user_id = sp.current_user()["id"]
playlist_name = f"{date} Billboard 100"
play_list = sp.user_playlist_create(user_id, playlist_name, public=False)

# Adding songs found into the new playlist
sp.playlist_add_items(play_list['id'], track_uris)
