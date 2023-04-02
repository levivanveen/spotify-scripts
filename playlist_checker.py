def playlist_list(api, playlist_name):
  playlists = []
  while True:
    results = api.sp.current_user_playlists(limit=50, offset=len(playlists))
    playlists.extend(results['items'])
    if results['next'] == None:
      break
  matching_playlists = [item for item in playlists if playlist_name.lower() in item['name'].lower() and item['owner']['id'] == api.username]
  return matching_playlists
  
def playlist_songs(api, playlists, song_name):
  found_pl = []
  bar_length = 100
  bar = get_bar(0, bar_length)

  song_total = sum([playlist['tracks']['total'] for playlist in playlists])
  songs_checked = 0

  print_prog('Searching playlists', bar, song_total, songs_checked)

  for i, playlist in enumerate(playlists):
    songs_checked_in_pl = 0

    results = api.sp.playlist_tracks(playlist['id'])
    tracks = results['items']

    while True:
      songs_checked += len(tracks) - songs_checked_in_pl
      songs_checked_in_pl = len(tracks)
      progress = songs_checked/song_total
      bar = get_bar(progress, bar_length)
      print_prog(f'Searching playlist {i+1}/{len(playlists)}: {playlist["name"]}', bar, song_total, songs_checked)

      if results['next'] == None:
        break
      results = api.sp.next(results)
      tracks.extend(results['items'])

    for track in tracks:
      if track is not None and 'track' in track and track['track'] is not None and track['track']['name'].lower() == song_name.lower():
        found_pl.append(playlist['name'])
        break


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

def print_prog(text, bar, total, prog):
  print(f"\r{text[:60]:<60} [{bar}] {prog}/{total}", end="", flush=True)
  return

def get_bar(prog, bar_len):
  fill = int(round(bar_len * prog))
  bar = '\u2588' * fill + '-' * (bar_len - fill)
  return bar