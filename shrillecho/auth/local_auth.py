import base64
import json
import random
import string
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import urllib.parse
import requests


def generate_random_string(length):
    """Generate a random string of specified length."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def authenticate_url(sp_auth):
 
    state = generate_random_string(16)

    spotify_authorize_url = 'https://accounts.spotify.com/authorize?' + urllib.parse.urlencode({
        'response_type': 'code',
        'client_id': sp_auth.client_id,
        'scope': sp_auth.scope,
        'redirect_uri': sp_auth.redirect_uri,
        'state': state
    })

    return spotify_authorize_url


sp_auth_obj = None

class RequestHandler(BaseHTTPRequestHandler):
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
                'redirect_uri': sp_auth_obj.redirect_uri,
                'grant_type': 'authorization_code',
            },
            'headers': {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic ' + base64.urlsafe_b64encode(f"{sp_auth_obj.client_id}:{sp_auth_obj.client_secret}".encode()).decode()
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

def run_server():
    with HTTPServer(('localhost', 8081), RequestHandler) as server:
        print('Starting server, use <Ctrl-C> to stop')
        server.serve_forever()

def authenticate_local(sp_auth):
    global sp_auth_obj
    sp_auth_obj = sp_auth
    webbrowser.open(authenticate_url(sp_auth))
    run_server()