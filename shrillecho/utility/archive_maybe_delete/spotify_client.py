import random
from typing import Tuple
import requests


class SpotifyClientGlitch:
    __client_id = ''
    __access_token = ''
    __client_token = ''

    def __init__(self, sp_dc: str = None, sp_key: str = None):
      

        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-language': 'en-GB,en;q=0.5',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Origin': 'https://open.spotify.com',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requets': '1',
            'Te': 'trailers',
            'Alt-Used': 'open.spotify.com',
            'Host': 'open.spotify.com',
            'Connection': 'keep-alive'
        }

        self.__api_root = 'https://api.spotify.com/v1'
        self.__web_root = 'https://open.spotify.com'

        self.__dc = sp_dc
        self.__key = sp_key

        self.access_token = None
        self.__session = None

        self.setup_tokens()

    def setup_tokens(self):
        self.access_token, self.__client_id = self.get_access_token()
        # self.access_token = self.get_access_token()
        self.client_token = self.get_client_token(self.__client_id)
        

    def get_access_token(self) -> Tuple[str, str]:
        with requests.session() as session:
            session.headers = self.__headers

    
            # cookies = {
            #         "sp_key": "2fcbc265-ee10-46bb-aeba-3103e6fd364a",
            #         "sp_dc": "AQBBCb1uk5chw2ky-YnNe1e5fibnlY6eR5NX9R0rMRomrFMh9o7t4gUK0ZsINCIM4qK-g8q2z0f3-M2TA6NYzyIwOUzyAgFJHmwsjRa74TFhBy7fFmAo8lmU5fhAqC_u6l4TmetSJ01OOIRghLTXzwxPlwxgU0I_",
            #     }

            cookies = {}

            resp = session.get(f'{self.__web_root}/get_access_token', verify=True, cookies=cookies)
            resp_json = resp.json()
           
            # return resp_json['accessToken'], resp_json['clientId']
            return resp_json['accessToken'], resp_json['clientId']

    def get_client_token(self, client_id: str):
        with requests.session() as session:
            session.headers = { 
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
                    "Accept": "application/json"
            }

            data = {
                "client_data": {
                    "client_version": "1.2.34.773.g9d8406e5",
                    "client_id": client_id,
                    "js_sdk_data": {
                        "device_brand": "unknown",
                        "device_model": "unknown",
                        "os": "windows",
                        "os_version": "NT 10.0",
                        "device_id": "f026e7d381f4aa57c9b21681ef16c106",
                        "device_type": "computer"
                    }
                }
            }

            resp = session.post('https://clienttoken.spotify.com/v1/clienttoken', json=data)
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
