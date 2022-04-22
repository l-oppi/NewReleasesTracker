import os
import requests
from datetime import datetime
from typing import Union
import utils
from token_refresher import SpotifyTokenRefresher

artists_data_path = 'include/artists_data.json'
artists_list_path  = 'include/artists_list.json'

class SpotifyReleasesTracker:
    def __init__(self) -> None:
        self.artists = utils.from_obj(artists_list_path, "artists")
        self.artists_data = utils.open_json(artists_data_path)

    def get_artist_code(self, artist) -> str:
        token = SpotifyTokenRefresher.refresh()
        url = "https://api.spotify.com/v1/search"
        params = {"q": artist, "type":"artist"}
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, params=params, headers=headers)
        n = 0
        found = False
        bad_search = False
        while not found:
            loc = response.json()['artists']["items"][n]
            if loc["name"].title() == artist.title():
                artist_id = loc["id"]
                found = True
            else:
                n += 1
            if n == 49:
                found = True
                bad_search = True
        if bad_search:
            raise Exception("Are you sure the artist name is right? We couldn't find it.")
        if not bad_search:
            return artist_id
        
    def get_most_recent_album(self, artist_id) -> Union[datetime, str, str]:
        token = SpotifyTokenRefresher.refresh()
        url = f"https://api.spotify.com/v1/artists/{artist_id}/albums" 
        ''' 
        If you want to set a specific type(album, single, compliation) and market use like the following: {"limit": 50, "include_groups": "album","market": "BR"}
        '''
        params = {"limit": 50}
        headers = {"Authorization": "Bearer " + token}
        response = requests.get(url, params=params, headers=headers)
        loc = response.json()
        albums = {}
        one_album = {}
        if len(loc["items"]) != 0:
            for i in loc["items"]:
                if "release_date" in i:
                    if len(i["release_date"]) == 10:
                        release_date = datetime.strptime(i["release_date"], "%Y-%m-%d")
                    elif len(i["release_date"]) == 7:
                        release_date = datetime.strptime(i["release_date"], "%Y-%m")
                    elif len(i["release_date"]) == 4:
                        release_date = datetime.strptime(i["release_date"], "%Y")
                else:
                    release_date = None
                if "album_type" in i:
                    one_album["album_type"] = i["album_type"]
                else:
                    one_album["album_type"] = None
                if "name" in i:
                    one_album["album_name"] = i["name"]
                else: 
                    one_album["album_name"] = ""
                    albums[release_date] = one_album
            if release_date != None:
                latest_release = max(albums.keys())
            else:
                latest_release = release_date
        else:
            latest_release = None
            albums[latest_release]["album_name"] = ""
            albums[latest_release]["album_type"] = ""
        return latest_release, albums[latest_release]["album_name"], albums[latest_release]["album_type"]
        
    def add_artist(self, artist):
        artist_id = self.get_artist_code(artist)
        latest_date, latest_name, latest_type = self.get_most_recent_album(artist_id)
        if latest_date != None:
            release_date = datetime.timestamp(latest_date)
        else:
            release_date = 0
        path_exists = False
        if os.path.isfile(artists_data_path):
            path_exists = True
        else:
            artistJson = {"artists": {}}
            utils.save_json(artists_data_path, artistJson)
            path_exists = True
        if path_exists:
            data = utils.open(artists_data_path)
            data["artists"][artist] = {
                "artist_id": artist_id,
                "release_date": release_date,
                "release_name": latest_name,
                "album_type": latest_type
                }
            utils.save_json(artists_data_path, data)
            artists = utils.open(artists_list_path)
            if artist not in artists["artists"]:
                data["artists"].append(artist)
            utils.save_json(artists_list_path, artists)
                
    def remove_artist(self, artist):
        path_exists = False
        if os.path.isfile(artists_data_path):
            path_exists = True
        else:
            raise Exception("File artist.json does not exist.")
        if path_exists:
            data = utils.open_json(artists_data_path)
            if artist in data["artists"].keys():
                data["artists"].pop(artist)
            else:
                raise Exception("No such artist to be removed!")
            utils.save_json(artists_data_path, data)
            artists = utils.open_json(artists_data_path)
            if artist in artists["artists"]:
                artists["artists"].remove(artist)
            else:
                raise Exception("No such artist to be removed from the list!")
            utils.save_json(artists_list_path, artists)
                
    def update_artist(self, artist, latest_date, latest_name, latest_type):
        if os.path.isfile(artists_data_path):
            data = utils.open_json(artists_data_path)
            data["artists"][artist]["release_date"] = datetime.timestamp(latest_date)
            data["artists"][artist]["release_name"] = latest_name
            data["artists"][artist]["album_type"] = latest_type
            utils.save_json(artists_data_path, data)
        else:
            raise Exception("File artist.json does not exist.")


    def get_artist_saved(self, artist):
        path_exists = False
        if os.path.isfile(artists_data_path):
            path_exists = True
        else:
            raise Exception("File artist.json does not exist")
        if path_exists:
            data = utils.open_json(artists_data_path)
        current_release = {
            artist:{
                "artist_id":  data["artists"][artist]["artist_id"],
                "release_date": data["artists"][artist]["release_date"],
                "release_name": data["artists"][artist]["release_name"],
                "album_type": data["artists"][artist]["album_type"]
            }
        }
        return current_release

    def compare_releases(self, artist):
        current_information = self.get_artist_saved(artist)
        artist_id = current_information[artist]["artist_id"]
        get_date = current_information[artist]["release_date"]
        latest_date, latest_name, latest_type = self.get_most_recent_album(artist_id)
        
        if get_date < datetime.timestamp(latest_date):
            self.update_artist(artist, latest_date, latest_name, latest_type)
            latest_info = {
                artist: {
                    "latest_date":  datetime.strftime(latest_date, "%d/%m/%Y"),
                    "latest_name":latest_name,
                    "latest_type": latest_type
                }
            }
            return latest_info
        else:
            return None
        
    def gather_updates(self):
        artists_list = utils.from_obj(artists_list_path,"artists")
        newer = None
        updates = {}
        for artist in artists_list:
            newer = self.compare_releases(artist)
            if newer != None:
                updates[artist] = newer[artist]
        if len(updates) > 0:
            return updates
        else:
            return None
                
    def show_updates(self):
        updates = self.gather_updates()
        if updates != None:
            print(f"\nNew Releases for {utils.get_date('%d/%m/%Y')}:\n")
            for key in updates.keys():
                print(key, ":\n")
                print(f"-Album: {updates[key]['latest_name']}")
                print(f"-Release Date: {updates[key]['latest_data']}")
                print(f"-Release Type: {updates[key]['latest_type']}\n")
        else:
            print("\nThere were no new releases for today. :(\n")

    def show_current_releases(self):
        artists = utils.open_json(artists_list_path)
        data = utils.open_json(artists_data_path)
        choosen = False
        while not choosen:
            for index, artist in enumerate(artists["artists"]):
                print(f"{index + 1} - {artist}")
            choice = input("\nWich artist do you want to see?\n")
            if choice not in artists["artists"]:
                print("\nChoose one of the following options!\n")
            else:
                target_artist = data["artists"][choice]
                choosen = True
        print(f"\n{choice} latest release: \n")
        print(f"-Album: {target_artist['release_name']}")
        print(f"-Release Date: {utils.epoch_to_string(target_artist['release_date'])}")
        print(f"-Release Type: {target_artist['album_type']}\n")
                
    def select_function(self, choice):
        if choice == '1':
            new_artist = input("\nNew artist name:")
            self.add_artist(new_artist)
            print("\nNew artist added!")
        elif choice == '2':
            unwanted_artist = input("\nArtist to be removed")
            self.remove_artist(unwanted_artist)
            print("\nArtist removed!")
        elif choice == '3':
            print("\nFetching updates...")
            self.show_updates()
        elif choice == '4':
            print("\nList of current artists:\n")
            self.show_current_releases()
        else:
            raise Exception("Choose a correct option!")  

def main():
    spt = SpotifyReleasesTracker()
    options = [
        "1 - Add artist",
        "2 - Remove artist",
        "3 - Show latest releases",
        "4 - Show artist current release"
        ]
    print("\nWelcome to the Artist Daily Update!\n")
    choosen = False
    while not choosen:
        for option in options:
            print(option)
        choice = input("\nYour choice: ")
        if choice not in ['1', '2', '3', '4']:
            print("\nChoose one of the following options!\n")
        else:
            choosen = True
    spt.select_function(choice)


if __name__ == '__main__':
    main()