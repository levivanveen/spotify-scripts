import psycopg2
from psycopg2 import IntegrityError

# Constants
HOST = 'localhost'
DATABASE = 'spotify'
USER = 'postgres'

class Db:
  def __init__(self) -> None:
    self.host = HOST
    self.database = DATABASE
    self.user = USER
    self.password = None
    self.conn = None
    self.cur = None

  def connect(self):
    try:
      self.conn = psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password)
      self.cur = self.conn.cursor()
    except psycopg2.Error:
      raise ValueError("Unable to connect to database")

  def close(self):
    self.cur.close()
    self.conn.close()

  def commit(self):
    self.conn.commit()

  def exec(self, query, values=None):
    try:
      self.cur.execute(query, values)
    except IntegrityError as e:
      self.conn.rollback()
      return False
    return True

  def exec_with_return(self, query, values=None):
    try:
      self.cur.execute(query, values)
    except IntegrityError as e:
      self.conn.rollback()
      return False
    return self.cur.fetchall()

  def update(self, query, values=None):
    self.cur.execute(query, values)
    self.commit()

  def get_user_id(self, spotify_id):
    return self.exec_with_return("SELECT id FROM account WHERE spotify_id = %s", (spotify_id,))[0][0]

  def add_playlists(self, p, sp_id):
    count = 0
    for i, playlist in enumerate(p):
      success = self.exec("INSERT INTO playlist (name, id, user_id, track_count) VALUES (%s, %s, %s, %s)",
                         (playlist['name'], playlist['id'], sp_id, playlist['tracks']['total']))
      if not success:
        self.update_track_count(playlist)
        continue
      self.commit()
      count += 1
      print(f"Playlist {playlist['name']} inserted successfully")
    return count

  def update_track_count(self, p):
    p_id = p['id']
    track_count = p['tracks']['total']
    self.update("UPDATE playlist SET track_count = %s WHERE id = %s", (track_count, p_id))
    self.commit()

  def add_songs(self, p, api):
    count = 0
    p_count = 0
    for playlist in p:
      p_id = playlist['id']
      results = api.get_sp().playlist_tracks(p_id)
      tracks = results['items']

      # Get all songs for playlist, put all results into tracks
      while True:
        if results['next'] == None:
          break
        results = api.get_sp().next(results)
        tracks.extend(results['items'])

      for track in tracks:
        if track is None or 'track' not in track or track['track'] is None:
          continue
        track_id = track['track']['id']
        track_name = track['track']['name']
        artist_name = track['track']['artists'][0]['name']
        album_name = track['track']['album']['name']
        # Add song to songs table
        try:
          self.exec("INSERT INTO songs (id, name, artist, album) VALUES (%s, %s, %s, %s)",
                           (track_id, track_name, artist_name, album_name))
          self.commit()
          count += 1
        except IntegrityError:
          self.conn.rollback()

        # Add song to playlist_songs table
        try:
          self.exec("INSERT INTO playlist_songs (playlist_id, id) VALUES (%s, %s)",
                           (p_id, track_id))
          self.commit()
          p_count += 1
        except IntegrityError:
          self.conn.rollback()
    return count, p_count

  def add_user(self, sp_id, sp_name, lfm_username):
    success = self.exec("INSERT INTO account (spotify_id, spotify_name, lastfm_username) VALUES (%s, %s, %s)",
                       (sp_id, sp_name, lfm_username))
    if not success:
      return False
    self.commit()
    return True


  def get_playlists(self, sp_id, name=''):
    if name:
      playlists = self.exec_with_return("SELECT id, name, track_count FROM playlist WHERE user_id = %s AND LOWER(name) LIKE %s", (sp_id, '%' + name.lower() + '%'))
    else:
      playlists = self.exec_with_return("SELECT id, name, track_count FROM playlist WHERE user_id = %s", (sp_id,))
    return playlists

  def get_playlist_songs(self, p_id):
    songs = self.exec_with_return("SELECT songs.id, songs.name FROM songs JOIN playlist_songs ON songs.id = playlist_songs.id WHERE playlist_songs.playlist_id = %s", (p_id,))
    return songs
  
  #def get_tracks 
