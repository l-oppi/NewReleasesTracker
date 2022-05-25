
import requests
import utils


class SpotifyTokenRefresher:
    def __init__(self) -> None:
        self.base_64: str = utils.from_obj("CONFIG.json", "base_64")
        self.refresh_token: str = utils.from_obj(
                                    "CONFIG.json",
                                    "refresh_token"
                                )

    def refresh(self) -> str:
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        headers = {
            "Authorization": f"Basic {self.base_64}"
        }
        response = requests.post(
                    "https://accounts.spotify.com/api/token",
                    data=data,
                    headers=headers
                )
        utils.debug_json(response.json())
        return response.json()["access_token"]


if __name__ == "__main__":
    utils.debug_json(SpotifyTokenRefresher().refresh())
