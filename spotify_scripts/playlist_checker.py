def playlist_list(api, playlist_name=""):
  playlists = []
  while True:
    results = api.get_sp().current_user_playlists(limit=50, offset=len(playlists))
    playlists.extend(results['items'])
    if results['next'] == None:
      break
  matching_playlists = [item for item in playlists if playlist_name.lower() in item['name'].lower() and item['owner']['id'] == api.get_sp_id()]
  return matching_playlists
  
def playlist_songs(db, playlists, song_name):
  found_pl = []
  bar_length = 100
  bar = get_bar(0, bar_length)

  song_total = sum([p[db.track_count_idx] for p in playlists])
  songs_checked = 0

  for i, playlist in enumerate(playlists):
    tracks = db.get_playlist_songs(playlist[db.playlist_id_idx])
    for track in tracks:
      if track[db.song_name_idx] is not None and track[db.song_name_idx].lower() == song_name.lower():
        found_pl.append(playlist[db.playlist_name_idx])
        break
    songs_checked += playlist[db.track_count_idx]
    progress = songs_checked/song_total
    bar = get_bar(progress, bar_length)

  #Print results of search
  print_prog(f'\rSearching playlist {i+1}/{len(playlists)}: {playlist[db.playlist_name_idx]}', bar, song_total, songs_checked)
  print_results(found_pl, song_name)
  return

def playlist_artists(db, playlists, artist_name):
  found_pl = []
  found_pl_ids = []
  bar_length = 100
  bar = get_bar(0, bar_length)

  song_total = sum([p[db.track_count_idx] for p in playlists])
  songs_checked = 0

  for i, playlist in enumerate(playlists):
    tracks = db.get_playlist_songs(playlist[db.playlist_id_idx])
    for track in tracks:
      if track[db.song_artist_idx] is not None and track[db.song_artist_idx].lower() == artist_name.lower():
        # Add playlist id and name to found_pl
        found_pl.append(playlist[db.playlist_name_idx])
        found_pl_ids.append(playlist[db.playlist_id_idx])
        break
    songs_checked += playlist[db.track_count_idx]
    progress = songs_checked/song_total
    bar = get_bar(progress, bar_length)
  
  #Print results of search
  print_prog(f'\rSearching playlist {i+1}/{len(playlists)}: {playlist[db.playlist_name_idx]}', bar, song_total, songs_checked)
  print_results(found_pl, artist_name)
  while True:
    choice = input("Enter playlist number to see specific songs. Enter to continue: ")
    try: choice = int(choice)
    except ValueError: choice = ""
    if (choice == ""): break
    elif (choice > len(found_pl) or choice < 1):
      print("Invalid choice")
      continue
    else:
      print()
      print(f"Songs in {found_pl[choice-1]}")
      print("--------------------------------------")
      songs = db.get_playlist_songs(found_pl_ids[choice-1])
      for song in songs:
        if (song[db.song_artist_idx] == artist_name):
          print(song[db.song_name_idx])
      print("--------------------------------------")
      print()
  return

def print_prog(text, bar, total, prog):
  print(f"\r{text[:60]:<60} [{bar}] {prog}/{total}", end="", flush=True)
  return

def get_bar(prog, bar_len):
  fill = int(round(bar_len * prog))
  bar = '\u2588' * fill + '-' * (bar_len - fill)
  return bar

def print_results(found_playlists, name):
  print()
  print("--------------------------------------")
  if len(found_playlists) == 0:
    print(f"'{name}' is not in any of the playlists")
  else:
    print(f"'{name}' is in {len(found_playlists)} playlist{'s'*(len(found_playlists)>1)}")
  for i, playlist in enumerate(found_playlists):
    print(i + 1, playlist)

  print("--------------------------------------")