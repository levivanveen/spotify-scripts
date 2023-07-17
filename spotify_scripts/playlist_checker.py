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

  song_total = sum([p[2] for p in playlists])
  songs_checked = 0

  print_prog('Searching playlists', bar, song_total, songs_checked)

  for i, playlist in enumerate(playlists):
    tracks = db.get_playlist_songs(playlist[0])
    for track in tracks:
      if track[1] is not None and track[1].lower() == song_name.lower():
        found_pl.append(playlist[1])
        break
    songs_checked += playlist[2]
    progress = songs_checked/song_total
    bar = get_bar(progress, bar_length)
    print_prog(f'\rSearching playlist {i+1}/{len(playlists)}: {playlist[1]}', bar, song_total, songs_checked)
  
  #Print results of search
  print()
  print("--------------------------------------")
  if len(found_pl) == 0:
    print(f"'{song_name}' is not in any of the playlists")
  else:
    print(f"'{song_name}' is in {len(found_pl)} playlist{'s'*(len(found_pl)>1)}")
  for i, playlist in enumerate(found_pl):
    print(i + 1, playlist)

  print("--------------------------------------")
  return

def playlist_artists(db, playlists, artist_name):
  found_pl = []
  bar_length = 100
  bar = get_bar(0, bar_length)

  song_total = sum([p[2] for p in playlists])
  songs_checked = 0

  print_prog('Searching playlists', bar, song_total, songs_checked)

  for i, playlist in enumerate(playlists):
    tracks = db.get_playlist_songs(playlist[0])
    for track in tracks:
      if track[2] is not None and track[2].lower() == artist_name.lower():
        found_pl.append(playlist[1])
        break
    songs_checked += playlist[2]
    progress = songs_checked/song_total
    bar = get_bar(progress, bar_length)
    print_prog(f'\rSearching playlist {i+1}/{len(playlists)}: {playlist[1]}', bar, song_total, songs_checked)
  
  #Print results of search
  print()
  print("--------------------------------------")
  if len(found_pl) == 0:
    print(f"'{artist_name}' is not in any of the playlists")
  else:
    print(f"'{artist_name}' is in {len(found_pl)} playlist{'s'*(len(found_pl)>1)}")
  for i, playlist in enumerate(found_pl):
    print(i + 1, playlist)

  print("--------------------------------------")
  return

def print_prog(text, bar, total, prog):
  print(f"\r{text[:60]:<60} [{bar}] {prog}/{total}", end="", flush=True)
  return

def get_bar(prog, bar_len):
  fill = int(round(bar_len * prog))
  bar = '\u2588' * fill + '-' * (bar_len - fill)
  return bar