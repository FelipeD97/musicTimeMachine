import requests
from bs4 import BeautifulSoup
import lxml
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

load_dotenv()

#### Scraping Billboard 100 site ####

date = input(
    "What year do you want to travel to? Type the date in this format, YYYY-MM-DD: "
)

URL = f"https://www.billboard.com/charts/hot-100/{date}/"

response = requests.get(URL)

soup = BeautifulSoup(response.text, "lxml")

song_titles = soup.select(selector="li .o-chart-results-list__item h3")
song_names = [song.get_text() for song in song_titles]
# print(song_names)

#### Spotify Authentication ####

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-public",
        redirect_uri="http://example.com",
        client_id=os.environ["SPOTIFY_CLIENT_ID"],
        client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
        show_dialog=True,
        cache_path=".cache",
    )
)

user_id = sp.current_user()["id"]
# print(user_id)

#### Grab Song URIs to pull spotify data ####

song_uris = []
year = date.split("-")[0]
for song in song_names:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    # print(result)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        # print(f"{song} doesn't exist in Spotify. Skipped.")
        pass

#### Creating Playlist ####

playlist = sp.user_playlist_create(
    user=user_id,
    name=f"{date} Billboard 100",
    description=f"These are the hottest songs on {date}.",
    public=True,
)
# print(playlist)

# print(song_uris)

#### Adding songs to playlist ####

playlist_id = playlist["id"]
sp.playlist_add_items(playlist_id=playlist_id, items=song_uris)

print(playlist["tracks"])
