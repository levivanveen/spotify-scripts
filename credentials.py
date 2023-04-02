import os

import spotipy
from dotenv import load_dotenv
from spotipy import util
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

#Constants
REDIRECT_URI = 'http://localhost:8080'
SCOPE = [
    'user-follow-read',
    'playlist-read-private',
    'playlist-read-collaborative',
    'user-library-read',
    'user-read-private',
    'user-read-email'
]
SIGN_IN_WEB = "1"
SIGN_IN_USER = "2"
SIGN_IN_DEFAULT = "3"


class SpotifyApi:
  def __init__(self) -> None:
    load_dotenv()
    self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
    self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    self.username = os.getenv('SPOTIFY_USER')
    self.scope = SCOPE
    self.redirect_uri = REDIRECT_URI
    self.sp = None
  
  def get_creds_web(self):
    try: 
      sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=self.client_id,
                                                  client_secret=self.client_secret,
                                                  redirect_uri=self.redirect_uri,
                                                  scope=self.scope))
      self.sp = sp
    except SpotifyException:
      raise ValueError("Unable to get web credentials")
  
  def get_creds_user(self, username):
    try:
      token = util.prompt_for_user_token(username, self.scope, client_id=self.client_id, client_secret=self.client_secret, redirect_uri=self.redirect_uri)
      if token:
        sp = spotipy.Spotify(auth=token)
        self.sp = sp
      else:
        raise ValueError("Token is empty")
    except SpotifyException:
      raise ValueError("Unable to get user credentials")


  def get_username(self):
    return self.username

  def valid_username(self, username):
    if self.sp == None:
      sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=self.client_id, client_secret=self.client_secret))
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
      self.username = username
    return valid
     

  def sign_in(self, sign_in):
    if sign_in == SIGN_IN_WEB:
      try:
        self.get_creds_web()
      except ValueError as e:
        print(e)
        return False

    elif sign_in == SIGN_IN_USER:
      newUsername = input("Enter your Spotify username or press enter to use the default: ")
      if newUsername != "":
        if self.set_username(newUsername) == False:
          return False
      try: 
        self.get_creds_user(self.get_username())
      except ValueError as e:
        print(e)
        return False

    elif sign_in == SIGN_IN_DEFAULT:
      if self.valid_username(self.get_username()) == False:
        return False
      try: 
        self.get_creds_user(self.get_username())
      except ValueError as e:
        print(e)
        return False
    return True
