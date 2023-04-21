from credentials import SpotifyApi


class UserInfo(SpotifyApi) :
  def __init__(self, api) -> None:
    super().__init__()
    self.sp = api.sp
    self.plays = self.sp.current_user_top_tracks(limit=50, time_range='medium_term')
    self.top_artists = self.sp.current_user_top_artists(limit=10)

  def print_user_info(self):
    print("Top Songs")
    print("--------------------------------------")
    for i, item in enumerate(self.plays['items']):
      print(i + 1, item['name'], "by", item['artists'][0]['name'])
    print("--------------------------------------")
    print("Top Artists")
    print("--------------------------------------")
    for i, item in enumerate(self.top_artists['items']):
      print(i + 1, item['name'])
    print("--------------------------------------")