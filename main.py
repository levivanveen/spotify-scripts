from credentials import SpotifyApi
from db_manager.database import Db
from spotify_scripts.playlist_checker import playlist_songs, playlist_artists
from spotify_scripts.user_info import UserInfo


def main():

  api = SpotifyApi()
  api.sign_in()
  
  db = load_db()
  user_id = db.get_user_id(api.get_sp_id())

  while(True):
    com = input("What function would you like to use? Enter to exit\n(1)Check playlist(s) for song\n(2)Check playlist(s) for artist\n(3)Top Songs and Artists\n:")
    print()
    if com == "": break
    elif com == "1":
      print("Check Playlist(s) for song")
      print("--------------------------------------")

      song_name = input("Song you want to check: ")
      playlist_name = input("Name of the playlist(s) you want to check, Enter to check all: ")
      print()
      playlists = db.get_playlists(user_id, playlist_name)
      print(f"{len(playlists)} Matching playlists:")
      for p in playlists:
        print(p[1])
      print()
      playlist_songs(db, playlists, song_name)

    ##COM IS 2
    elif com == "2":
      print("Check Playlist(s) for artist")
      print("--------------------------------------")

      artist_name = input("Artist you want to check: ")
      playlist_name = input("Name of the playlist(s) you want to check, Enter to check all: ")
      print()
      playlists = db.get_playlists(user_id, playlist_name)
      print(f"{len(playlists)} Matching playlists:")
      for p in playlists:
        print(p[1])
      print()
      playlist_artists(db, playlists, artist_name)
    elif com == "3":
      print("Get top songs and artists")
      print("--------------------------------------")

      user = UserInfo(api)
      user.print_user_info()

  db.close()

def load_db():
  db = Db()
  try:
    db.connect()
  except ValueError:
    exit(1)
  return db

if __name__ == '__main__':
  main()