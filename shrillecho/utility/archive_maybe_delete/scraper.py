import os

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from shrillecho.utility.archive_maybe_delete import general as sh
import re


class Scraper:
    def __init__(self):
        self.__driver = self.setup_driver()

    def get_driver(self):
        return self.__driver

    def wait_on_load(self, driver, pattern):
        page_source = driver.page_source
        matches = set(re.findall(pattern, page_source))
        return len(matches) > 1

    def fetch_radio_seed_en(self, driver, track):
        url = f'https://everynoise.com/research.cgi?mode=radio&name=spotify:track:{track}'
        driver.get(url)
        pattern = r'trackid="([\w]+)"'
        matches = set(re.findall(pattern, driver.page_source))

        tracks = []
        for match in matches:
            tracks.append(f'spotify:track:{match}')
        return tracks

    def fetch_source(self, driver, uri, pattern):
        driver.get(f'{uri}')
        WebDriverWait(driver, 10).until(lambda driver=driver: self.wait_on_load(driver, pattern))
        return driver.page_source

    def cache(self, path, mode, content=None):
        if not os.path.exists('cache'):
            os.makedirs('cache')

        with open(path, mode, encoding='utf-8') as cache:
            if mode == 'r':
                return cache.read()
            elif mode == 'w':
                cache.write(content)

    def get_followers(self, seed_user: str, use_cache=True):
        base_uri = 'https://open.spotify.com/user'
        uri = f'{base_uri}/{seed_user}/followers'
        hashed_uri = sh.hash_str(uri)
        pattern = r'/user/(\w+)'

        cache_path = os.path.join('cache', hashed_uri)

        if os.path.exists(f'cache/{hashed_uri}') and use_cache:
            sh.log(message='Using cached response...')
            return set(re.findall(pattern, self.cache(cache_path, 'r')))

        source = self.fetch_source(self.__driver, uri, pattern)

        self.cache(cache_path, 'w', content=source)

        return set(re.findall(pattern, source))

    def get_playlists(self, driver):
        pattern = r'/playlist/(\w+)'
        WebDriverWait(driver, 10).until(lambda driver=driver: re.search(pattern, driver.page_source))
        source = driver.page_source
        matches = re.findall(pattern, source)
        return matches
    
    def get_Tracks(self, driver):
        pattern = r'/track/(\w+)'
        WebDriverWait(driver, 10).until(lambda driver=driver: re.search(pattern, driver.page_source))
        source = driver.page_source
        matches = re.findall(pattern, source)
        return matches

    def setup_driver(self) -> WebDriver:
        # Define the options for Firefox, including the headless mode
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.add_argument('--headless')

        service = Service()
        return webdriver.Firefox(service=service, options=firefox_options)

    def add_cookies(self, driver, sp_dc, sp_key):
        cookies = [
            {
                "name": "sp_dc",
                "value": sp_dc,
                "domain": "open.spotify.com"
            },
            {
                "name": "sp_key",
                "value": sp_key,
                "domain": "open.spotify.com"
            },
        ]

        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.refresh()
