import os
import time
import json
import platform
from time import perf_counter
from typing import List, Union
import logging
from dotenv import load_dotenv, dotenv_values

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebDriver



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

    def create_browser(self) -> Union[ChromeWebDriver, FirefoxWebDriver]:
        os_type = platform.system()
        os_browsers = {'Linux': 'Firefox', 'Windows': 'Chrome'}
        if os_type not in os_browsers:
            return None
        logging.info('Start creating %s browser.', os_browsers[os_type])
        time_start = perf_counter()
        if os_type == 'Linux':
            options = webdriver.FirefoxOptions()
            options.add_argument('-headless')
            options.add_argument('window-size-1920x935')
            browser = webdriver.Firefox(options=options)
        else:
            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            options.add_argument('window-size-1920x935')
            browser = webdriver.Chrome(options=options)
        time_stop = perf_counter() - time_start
        logging.info(
            '%s browser was created successfully in %.1f ms.',
            os_browsers[os_type],
            time_stop*1e3
        )
        return browser


    # def create_chrome_browser(self) -> ChromeWebDriver:
    #     logging.info('Start creating chrome browser.')
    #     time_start = perf_counter()
    #     options = webdriver.ChromeOptions()
    #     options.add_argument('headless')
    #     options.add_argument('window-size-1920x935')
    #     browser = webdriver.Chrome(options=options)
    #     time_stop = perf_counter() - time_start
    #     logging.info(
    #         'Chrome browser was created successfully in %.1f ms.',
    #         time_stop*1e3
    #     )
    #     return browser

    # def create_firefox_browser(self) -> FirefoxWebDriver:
    #     logging.info('Start creating Firefox browser.')
    #     time_start = perf_counter()
    #     options = webdriver.FirefoxOptions()
    #     options.add_argument('-headless')
    #     options.add_argument('window-size-1920x935')
    #     browser = webdriver.Firefox(options=options)
    #     time_stop = perf_counter() - time_start
    #     logging.info(
    #         'Firefox browser was created successfully in %.1f ms.',
    #         time_stop*1e3
    #     )
    #     return browser

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
        browser = staff_parser.create_firefox_browser()
        # browser = staff_parser.create_chrome_browser()
        cookies = staff_parser.get_cookies(browser, url)
        # staff_parser.export_cookies(cookies, 'cookies.json')

    def str_cookies(self) -> str:
        cookies = self.import_cookies('cookies.json')
        not_google_cookies = [el for el in cookies if not el.get('name', '').startswith('_')]
        print(len(not_google_cookies))
        one_line_cookie = json.dumps(cookies)
        print(type(one_line_cookie))
        self.add_cookies_to_dotenv_file('.env', not_google_cookies)

    def add_cookies_to_dotenv_file(self, filename: str, cookies: List[dict]) -> None:
        str_cookies = json.dumps(cookies)
        with open(filename, 'r') as f:
            j = None
            for i, line in enumerate(f):
                if line.startswith('COOKIES'):
                    j = i
                    break
            print(f'{j = }')
            print(type(enumerate(f)))
            print(f.readline())



        with open(filename, 'a') as f:
            f.write(f'\nCOOKIES={str_cookies}')
        load_dotenv()
        print(dotenv_values())


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
    staff_parser.create_browser()
    # staff_parser.str_cookies()
    # staff_parser.get_staff(URL)

if __name__ == '__main__':
    test()
