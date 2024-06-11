import os
import time
import json
from time import perf_counter
from typing import List
import logging
from dotenv import load_dotenv, dotenv_values

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver 



logging.basicConfig(
    format='%(asctime)s %(levelname)s:\t%(message)s',
    # level=logging.DEBUG
    level=logging.INFO
)



class StaffParser:

    def __init__(self) -> None:
        self._load_dotenv('./.env')

    def _load_dotenv(self, path_: str) -> None:
        load_dotenv(os.path.abspath(path_))
        logging.debug('dotenv values: %s', dotenv_values())

    def create_chrome_browser(self) -> ChromeWebDriver:
        logging.info('Start creating chrome browser.')
        time_start = perf_counter()
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size-1920x935')
        browser = webdriver.Chrome(options=options)
        time_stop = perf_counter() - time_start
        logging.info(
            'Chrome browser was created successfully in %.1f ms.',
            time_stop*1e3
        )
        return browser

    def get_cookies(self, browser: ChromeWebDriver, url: str) -> dict:
        logging.info('Start getting cookies.')
        time_start = perf_counter()
        browser.get(url)
        time_stop = perf_counter() - time_start
        logging.info(
            'Cookies were got successfully in %.1f ms.',
            time_stop*1e3
        )
        return browser.get_cookies()

    def export_cookies(self, cookies: dict, filename: str) -> None:
        try:
            with open(filename, 'w') as f:
                json.dump(cookies, f, indent=4)
            logging.info('Cookies have been saved at %s.', filename)
        except IOError:
            logging.error(
                'Cannot create file. Check file name: %s',
                filename
            )

    def import_cookies(self, filename: str) -> dict:
        cookies = {}
        try:
            with open(filename, 'r') as f:
                cookies = json.load(f)
            logging.info('Cookies have been read from %s', filename)
        except IOError:
            logging.info('Unable to find file: %s.')
        return cookies

    def get_staff(self, url: str) -> None:
        staff_parser = StaffParser()
        browser = staff_parser.create_chrome_browser()
        cookies = staff_parser.get_cookies(browser, url)
        staff_parser.export_cookies(cookies, 'cookies.json')

    def parse_url(self, url: str) -> None:
        logging.info('Start parsing url: %s', url)
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size-1920x935')
        browser = webdriver.Chrome(options=options)
        browser.get(url)
        logging.info('Parsing finished successfully: %s', url)



def test():
    URL = 'https://jiht.ru/'
    staff_parser = StaffParser()
    staff_parser.get_staff(URL)

if __name__ == '__main__':
    test()
