from credentials import SpotifyApi
from db_manager.database import Db
from main import load_db, sign_in
from spotify_scripts.playlist_checker import playlist_list
from spotify_scripts.user_info import UserInfo


def main():

  api = SpotifyApi()
  sign_in(api)

  db = load_db()

  print()
  method = input("What function would you like to use? Press enter to exit\n(1)Update user playlists\n(2)Add current user\n(3)Update playlist songs: ")
  print()
  if method == "": return
  elif method == "1":
    playlists = playlist_list(api)
    sp_id = db.get_user_id(api.get_sp_id())
    update_user_playlists(db, playlists, sp_id)
  elif method == "2":
    add_user(api, db)
  elif method == "3":
    sp_id = db.get_user_id(api.get_sp_id())
    playlists = playlist_list(api)
    update_user_playlists(db, playlists, sp_id)
    update_playlist_songs(db, playlists, api)

  db.close()
  return

def update_user_playlists(db, playlists, sp_id):
  print("Added", db.add_playlists(playlists, sp_id), "playlists to database")

def add_user(api, db):
  added = db.add_user(api.get_sp_id(), api.get_sp_name(), api.get_lfm_username())
  if added:
    print("Added user to database")
  else:
    print("User already in database")

def update_playlist_songs(db, playlists, api):
  song_count, p_songs_count = db.add_songs(playlists, api)
  print("Added", song_count, "songs")
  print("Added", p_songs_count, "playlist songs")



if __name__ == '__main__':
  main()