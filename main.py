from credentials import SpotifyApi
from db_manager.database import Db
from spotify_scripts.playlist_checker import playlist_songs
from spotify_scripts.user_info import UserInfo


def main():

  api = SpotifyApi()
  sign_in(api)
  
  db = load_db()
  user_id = db.get_user_id(api.get_sp_id())

  while(True):
    com = input("What function would you like to use? Press enter to exit\n(1)Check playlist(s) for song\n(2)Top Songs and Artists\n:")
    print()
    if com == "": break
    if com == "1":
      print("Check Playlist(s) for song")
      print("--------------------------------------")

      song_name = input("Song you want to check: ")
      playlist_name = input("Name of the playlist(s) you want to check, press enter to check all: ")
      print()
      playlists = db.get_playlists(user_id, playlist_name)
      print(f"{len(playlists)} Matching playlists:")
      for p in playlists:
        print(p[1])
      print()
      playlist_songs(db, playlists, song_name)

    ##COM IS 2
    if com == "2":
      print("Get top songs and artists")
      print("--------------------------------------")

      user = UserInfo(api)
      user.print_user_info()

  db.close()

def load_db():
  db = Db()
  db.connect()
  return db

def sign_in(api):
  spotify_sign_in = False
  lastfm_sign_in = False
  while True:
    if not spotify_sign_in: spotify_sign_in = api.spotify_sign_in()
    if not lastfm_sign_in: lastfm_sign_in = api.lastfm_sign_in()
    if spotify_sign_in and lastfm_sign_in: break
    else:
      if not spotify_sign_in:
        print("Failed to sign in to Spotify. Retrying...")
      if not lastfm_sign_in:
        print("Failed to sign in to Last.fm. Retrying...")
      print()

if __name__ == '__main__':
  main()