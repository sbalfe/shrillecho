from base64 import urlsafe_b64encode
import base64
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import random
import string
import threading
import webbrowser
import requests
import spotipy
import os
import urllib.parse
import httpx



@dataclass
class SpotifyAuthContext:
    client_id: str
    client_secret: str
    scope: str
    redirect_uri: str


class SpotifyAuth:
    class RequestHandler(BaseHTTPRequestHandler):
        def __init__(self, auth_instance, *args, **kwargs):
            self.auth_instance = auth_instance
            super().__init__(*args, **kwargs)
            
        def do_GET(self):
            parsed_path = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed_path.query)
            code = query.get('code', [None])[0]
            state = query.get('state', [None])[0]

            if state is None:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"State mismatch error.")
                return
        
        
            auth_options = {
                'url': 'https://accounts.spotify.com/api/token',
                'data': {
                    'code': code,
                    'redirect_uri': self.auth_instance.redirect_uri,
                    'grant_type': 'authorization_code',
                },
                'headers': {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Authorization': 'Basic ' + base64.urlsafe_b64encode(f"{self.auth_instance.client_id}:{self.auth_instance.client_secret}".encode()).decode()
                }
            }

            response = requests.post(auth_options['url'], data=auth_options['data'], headers=auth_options['headers'])

            if response.ok:
                tokens = response.json()
                with open('.shrillecho_auth_cache', 'w') as file:
                    json.dump(tokens, file)

                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'<h1>Authorization successful. You can close this window.</h1>')

                threading.Thread(target=self.server.shutdown).start()  
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Failed to retrieve the access token from Spotify.")

    def __init__(self, client_id, client_secret, redirect_uri, scope):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope 

    def refresh_access_token(self, refresh_token):
        
        client_creds = f"{self.client_id}:{self.client_secret}"
        client_creds_b64 = urlsafe_b64encode(client_creds.encode()).decode()
        
        refresh_url = 'https://accounts.spotify.com/api/token'
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {client_creds_b64}"
        }
        body = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        response = requests.post(refresh_url, headers=headers, data=body)
        
        if response.status_code == 200:
        
            return response.json()
        else:
            return f"Failed to refresh token. Status code: {response.status_code}, Response: {response.text}", None

    def get_client_access_token(self):
        client_id = os.environ.get("SPOTIPY_CLIENT_ID")
        client_secret = os.environ.get("SPOTIPY_CLIENT_SECRET")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = urlsafe_b64encode(client_creds.encode()).decode()
        
        token_url = 'https://accounts.spotify.com/api/token'

        headers = {
            "Authorization": f"Basic {client_creds_b64}"
        }
        body = {
            "grant_type": "client_credentials"
        }
        
        response = requests.post(token_url, headers=headers, data=body)
        
        if response.status_code == 200:
            token_response_data = response.json()
            access_token = token_response_data['access_token']


            with open('.shrillecho_auth_cache', 'w') as file:
                json.dump(token_response_data, file)
            return access_token
        else:
            return f"Failed to obtain access token. Status code: {response.status_code}, Response: {response.text}"
    
    def authenticate_url(self):

        def generate_random_string(length):
            """Generate a random string of specified length."""
            return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        
        state = generate_random_string(16)
   
        spotify_authorize_url = 'https://accounts.spotify.com/authorize?' + urllib.parse.urlencode({
            'response_type': 'code',
            'client_id': self.client_id,
            'scope': self.scope,
            'redirect_uri': self.redirect_uri,
            'state': state
        })

        return spotify_authorize_url
    
    def auth_spotipy_client(access_token):
        return spotipy.Spotify(auth=access_token)
    

    def get_access_token(self, code):
        token_url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": "Basic " + base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode(),
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "code": code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }
        
        with httpx.Client() as client:
            response = client.post(token_url, headers=headers, data=data)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to get access token, status code: {response.status_code}")

    @staticmethod
    def run_server(auth_instance):
        handler = lambda *args, **kwargs: SpotifyAuth.RequestHandler(auth_instance, *args, **kwargs)
        with HTTPServer(('localhost', 8081), handler) as server:
            print('Starting server, use <Ctrl-C> to stop')
            server.serve_forever()

    def authenticate_local(self):
        webbrowser.open(self.authenticate_url())
        SpotifyAuth.run_server(self)

class OAuthCredentials:

    def __init__(self, auth_context: SpotifyAuthContext):

        self.auth = SpotifyAuth(auth_context.client_id, 
                                auth_context.client_secret, 
                                auth_context.redirect_uri, 
                                auth_context.scope)
    
    def get_access_token(self) -> str:
        if not os.path.exists('.shrillecho_auth_cache'):
            self.auth.authenticate_local()
        
        with open('.shrillecho_auth_cache') as f:
            auth_cache = json.loads(f.read())
            return auth_cache['access_token']

class ClientCredentials:

    def __init__(self, auth_context: SpotifyAuthContext):
        self.auth = SpotifyAuth(auth_context.client_id, 
                                auth_context.client_secret, 
                                auth_context.redirect_uri, 
                                auth_context.scope)
    
    def get_access_token(self) -> str:
        return self.auth.get_client_access_token()
