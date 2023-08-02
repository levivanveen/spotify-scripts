import ast
import os
import time
import webbrowser

import pylast
import spotipy
from dotenv import load_dotenv
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from spotipy.util import prompt_for_user_token

#Constants
REDIRECT_URI = 'http://localhost:8080'
SCOPE = [
    'user-follow-read',
    'playlist-read-private',
    'playlist-read-collaborative',
    'user-library-read',
    'user-read-private',
    'user-read-email',
    'user-top-read',
]
SIGN_IN_WEB = "1"
SIGN_IN_USER = "2"
SIGN_IN_DEFAULT = "3"
AUTH_FOLDER = 'auth_cache'
SESSION_KEY_FILE = f'{AUTH_FOLDER}/.lfm-session_key'
SPOTIFY_CACHE = f'{AUTH_FOLDER}/.spotify-cache'
MAX_ATTEMPTS = 20


class SpotifyApi:
  def __init__(self) -> None:
    load_dotenv()
    self.spotify_id = os.getenv('SPOTIFY_CLIENT_ID')
    self.spotify_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    self.spotify_username = os.getenv('SPOTIFY_USER')
    self.lastfm_key = os.getenv('LASTFM_API_KEY')
    self.lastfm_secret = os.getenv('LASTFM_API_SECRET')
    self.scope = SCOPE
    self.redirect_uri = REDIRECT_URI
    self.sp = None
    self.lfm = None
    
    if not os.path.exists(AUTH_FOLDER):
      # Create the directory if it does not exist
      os.makedirs(AUTH_FOLDER)

  def get_sp_id(self):
    return self.spotify_username
  
  def get_lfm_username(self):
    return self.lfm.get_authenticated_user().get_name()

  def get_sp_name(self):
    return self.sp.current_user()['display_name']
  
  def get_sp(self):
    return self.sp

  def valid_username(self, username):
    if self.sp == None:
      sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=self.spotify_id, client_secret=self.spotify_secret))
    else:
      sp = self.sp

    try:
      sp.user(username)
      return True
    except SpotifyException:
      raise ValueError(f"The username {username} is not valid. Please try again.")

  def set_username(self, username):
    valid = self.valid_username(username)
    if valid:
      self.spotify_username = username
    return valid
     
  def sign_in(self):
    spotify_sign_in = False
    lastfm_sign_in = False
    while True:
      if not spotify_sign_in: spotify_sign_in = self.spotify_sign_in()
      if not lastfm_sign_in: lastfm_sign_in = self.lastfm_sign_in()
      if spotify_sign_in and lastfm_sign_in: break
      else:
        if not spotify_sign_in:
          print("Failed to sign in to Spotify. Retrying...")
        if not lastfm_sign_in:
          print("Failed to sign in to Last.fm. Retrying...")
        print()
    return self
     

  def spotify_sign_in(self):
    print()
    sign_in = input(f"How would you like to sign in to Spotify?\n(1)web\n(2)username\n(3)Use {self.spotify_username} as username\n:")
    print()
    if sign_in == "": return False

    if sign_in == SIGN_IN_WEB:
      try:
        self.get_creds_web()
        if self.set_username(self.sp.current_user()['id']) == False:
          return False
      except ValueError as e:
        print(e)
        return False

    elif sign_in == SIGN_IN_USER:
      newUsername = input("Enter your Spotify username or press enter to use the default: ")
      if newUsername != "":
        if self.set_username(newUsername) == False:
          return False
      try: 
        self.get_creds_user(self.spotify_username)
      except ValueError as e:
        print(e)
        return False

    elif sign_in == SIGN_IN_DEFAULT:
      if self.valid_username(self.spotify_username) == False:
        return False
      try: 
        self.get_creds_user(self.spotify_username)
      except ValueError as e:
        print(e)
        return False
    return True
  
  def lastfm_sign_in(self):
    saved_username = ""
    if os.path.exists(SESSION_KEY_FILE):
      with open(SESSION_KEY_FILE, 'r') as f:
        _, saved_username = ast.literal_eval(f.read())
    inputString = f" or press enter to use {saved_username}" if saved_username != "" else ""
    new_user = input(f"Signing into Last.fm\nEnter your Last.fm username {inputString}\n:")
    print()
    try:
      self.get_creds_lfm_web(new_user)
      return True
    except ValueError as e:
      print(e)
      return False

  def get_creds_web(self):
    try: 
      sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=self.spotify_id,
                                                  client_secret=self.spotify_secret,
                                                  redirect_uri=self.redirect_uri,
                                                  scope=self.scope))
      self.sp = sp
    except SpotifyException:
      raise ValueError("Unable to get web credentials")
  
  def get_creds_user(self, username):
    cache_path = f"{SPOTIFY_CACHE}-{username}"
    try:
      token = prompt_for_user_token(username, self.scope, self.spotify_id, self.spotify_secret, 
                                    self.redirect_uri, cache_path)
      if token:
        sp = spotipy.Spotify(auth=token)
        self.sp = sp
      else:
        raise ValueError("Token is empty")
    except SpotifyException:
      raise ValueError("Unable to get user credentials")

  def get_creds_lfm_web(self, username):
    network = pylast.LastFMNetwork(self.lastfm_key, self.lastfm_secret, username=username)
    try:
        with open(SESSION_KEY_FILE, 'r') as f:
            session_key, saved_username = ast.literal_eval(f.read())
            if username != "" and saved_username != username:
              raise ValueError("Username does not match the saved username")
            # Only set session key and username if they match given username
            network.session_key = session_key
            network.username = saved_username
            network.get_user('user')  # Test if session key is valid
    except (FileNotFoundError, ValueError, pylast.WSError):
        try:
            skg = pylast.SessionKeyGenerator(network)
            self._authorize_lfm_app(network, skg)
            with open(SESSION_KEY_FILE, 'w') as f:
                f.write(str((network.session_key, username)))
        except (pylast.WSError, ValueError):
            os.remove(SESSION_KEY_FILE)
            raise ValueError("Unable to get LastFM credentials")
    self.lfm = network
  
  def _authorize_lfm_app(self, network, skg):
    url = skg.get_web_auth_url()
    webbrowser.open(url)
    session_key_obtained = False
    for _ in range(MAX_ATTEMPTS):
      try:
        session_key = skg.get_web_auth_session_key(url)
        network.session_key = session_key
        network.get_user('user')  # Test if session key is valid
        session_key_obtained = True
        break
      except pylast.WSError:
        time.sleep(1)
    if not session_key_obtained:
      raise ValueError("Unable to get LastFM credentials")