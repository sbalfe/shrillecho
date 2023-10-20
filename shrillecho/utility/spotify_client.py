import random
from typing import Tuple

from requests import Session

from shrillecho.utility.general import (
    log
)
import requests


class SpotifyClient:
    __client_id = ''
    __access_token = ''
    __client_token = ''

    def __init__(self, sp_dc: str, sp_key: str):
        log("Setting up web client")

        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
            'Accept': 'application/json',
            'Origin': 'https://open.spotify.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Referer': 'https://open.spotify.com/',
            'Te': 'trailers',
            'App-Platform': 'WebPlayer'
        }

        self.__api_root = 'https://api.spotify.com/v1'
        self.__web_root = 'https://open.spotify.com'

        self.__dc = sp_dc
        self.__key = sp_key

        self.__session = None

        self.setup_tokens()

    def setup_tokens(self):
        self.__access_token, self.__client_id = self.get_access_token()
        self.__client_token = self.get_client_token(self.__client_id)

    def get_access_token(self) -> Tuple[str, str]:
        with requests.session() as session:
            session.headers = self.__headers

            cookie = {
                'sp_dc': self.__dc,
                'sp_key': self.__key
            }

            resp = session.get(f'{self.__web_root}/get_access_token', cookies=cookie, verify=True)
            resp_json = resp.json()
            return resp_json['accessToken'], resp_json['clientId']

    def get_client_token(self, client_id: str):
        with requests.session() as session:
            session.headers = self.__headers
            data = {
                "client_data": {
                    "client_version": "1.2.13.477.ga4363038",
                    "client_id": client_id,
                    "js_sdk_data":
                        {
                            "device_brand": "",
                            "device_id": "",
                            "device_model": "",
                            "device_type": "",
                            "os": "",
                            "os_version": ""
                        }
                }
            }

            resp = session.post('https://clienttoken.spotify.com/v1/clienttoken', json=data, verify=True)
            resp_json = resp.json()
            return resp_json['granted_token']['token']

    def __enter__(self):
        request = "displayproxies"
        protocol = "http"
        timeout = "10000"
        country = "GB"
        ssl = "all"
        anonymity = "all"

        proxies = requests.get(
            f'https://api.proxyscrape.com/v2/?request={request}&protocol={protocol}&timeout={timeout}&country={country}&ssl={ssl}&anonymity={anonymity}')

        http_proxy = proxies.text.split('\n')[random.randint(0,1)]

        self.__session = requests.Session()
        self.__session.headers = self.__headers
        self.__session.proxies = {
            "http": http_proxy
        }
        self.__session.headers.update({
            'Client-Token': self.__client_token,
            'Authorization': f'Bearer {self.__access_token}'
        })
        return self.__session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__session.close()
