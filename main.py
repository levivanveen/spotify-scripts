from credentials import SpotifyApi
from playlist_checker import playlist_list, playlist_songs


def main():
  while True:
    api = SpotifyApi()
    sign_in = input(f"How would you like to sign in?\n(1)web\n(2)username\n(3)Use {api.username} as username\n:")
    print()
    if sign_in == "": return
    if api.sign_in(sign_in) == True: break

  while(True):
    com = input("What function would you like to use? Press enter to exit\n(1)Check playlist(s) for song\n:")
    print()
    if com == "": return
    if com == "1":
      print("Check Playlist(s) for song")
      print("--------------------------------------")

      song_name = input("Song you want to check: ")
      playlist_name = input("Name of the playlist(s) you want to check, press enter to check all: ")
      print()
      playlists = playlist_list(api, playlist_name)
      print(f"{len(playlists)} Matching playlists:")
      for playlist in playlists:
        print(playlist['name'])
      print()
      playlist_songs(api, playlists, song_name)

if __name__ == '__main__':
  main()