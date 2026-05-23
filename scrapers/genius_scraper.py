from dotenv import load_dotenv
import os
from pubmed_scraper import save_to_json
import time

# import requests
# from rich import print

# from bs4 import BeautifulSoup
import lyricsgenius

load_dotenv()
token = os.getenv("GENIUS_TOKEN")


# def search_songs(query, max_results=1):
#     url = f"https://api.genius.com/search"
#     params = {"q": query}
#     headers = {"Authorization": f"Bearer {token}"}

#     response = requests.get(url, headers=headers, params=params)
#     hits = response.json()["response"]["hits"]

#     urls = [hit["result"]["url"] for hit in hits]

#     return urls


# songs = search_songs("rap")


# # def get_lyrics(url):
# #     response = requests.get(url)
# #     soup = BeautifulSoup(response.text, "html.parser")

# #     paragraphs = soup.find_all("p")
# #     print(paragraphs)


# # get_lyrics(songs[0])


genius = lyricsgenius.Genius(token, timeout=20)

artists = {
    "rap": ["Eminem", "Kendrick Lamar", "J. Cole"],
    "rock": ["Linkin Park", "Pearl Jam", "Nirvana"],
    "blues": ["B.B. King", "Muddy Waters", "Robert Johnson"],
}


def get_songs_bygenre(genre, max_songs_per_artists=5):
    songs = []
    for artist in artists[genre]:
        artist_songs = genius.search_artist(artist, max_songs=max_songs_per_artists)
        for song in artist_songs.songs:
            songs.append(song.lyrics)
        time.sleep(2)
    return songs


for genre in artists.keys():
    save_to_json(get_songs_bygenre(genre), f"data/raw/{genre}.json")
