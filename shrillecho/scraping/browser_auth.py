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

    def get(self, url):
        return self.__driver.get(url)
    

    def get_biscuits(self):
        return self.__driver.get_cookies()
    
    def setup_driver(self) -> WebDriver:
    
        firefox_options = webdriver.FirefoxOptions()
        # firefox_options.add_argument('--headless')

        service = Service()
        return webdriver.Firefox(service=service, options=firefox_options)

    def wait_on_load(self, driver, pattern):
        page_source = driver.page_source
        matches = set(re.findall(pattern, page_source))
        return len(matches) > 1
    
    def fetch_source(self, driver, uri, pattern):
        driver.get(f'{uri}')
        WebDriverWait(driver, 10).until(lambda driver=driver: self.wait_on_load(driver, pattern))
        return driver.page_source

    def get_followers(self, seed_user: str):
        base_uri = 'https://open.spotify.com/user'
        uri = f'{base_uri}/{seed_user}/followers'
        pattern = r'/user/(\w+)'
        source = self.fetch_source(self.__driver, uri, pattern)

        return set(re.findall(pattern, source))
    
    def add_cookies(self, sp_dc, sp_key):
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
            self.__driver.add_cookie(cookie)
        self.__driver.refresh()


