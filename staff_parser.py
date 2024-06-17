import os
import time
import json
import platform
from time import perf_counter
from typing import List, Union, Dict, Optional
import logging
from dotenv import load_dotenv, dotenv_values

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException




logging.basicConfig(
    format='%(asctime)s %(levelname)s:\t%(message)s',
    # level=logging.DEBUG
    level=logging.INFO
)



class StaffParser:

    # def __init__(self) -> None:
    #     self._load_dotenv_file('./.env')

    def _load_dotenv_file(self, path_: str) -> None:
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

    # def get_cookies(self, browser: ChromeWebDriver, url: str) -> dict:
    #     logging.info('Start getting cookies.')
    #     time_start = perf_counter()
    #     browser.get(url)
    #     time_stop = perf_counter() - time_start
    #     logging.info(
    #         'Cookies were got successfully in %.1f ms.',
    #         time_stop*1e3
    #     )
    #     return browser.get_cookies()

    def authorization_passed(self, browser, timeout_: int):
        try:
            element = WebDriverWait(browser, timeout_).until(
                EC.presence_of_element_located((By.CLASS_NAME, "auth-welcome"))
            )
            logging.info('Authorization was successful.')
            return True
        except TimeoutException:
            logging.error('Authorization failed. Check your username and password.')
            return False

    def update_dotenv_file(self, filename: str, data: Dict[str, str]):
        try:
            with open(filename, 'w') as f:
                for key, value in data.items():
                    f.write(f'{key}={value}\n')
            logging.info('`%s` was updated.', filename)
        except IOError:
            logging.error(
                'Cannot update file. Check file name: %s',
                filename
            )

    def log_in(self, browser, dotenv_file, url):
        # browser.get(url)
        self._load_dotenv_file(dotenv_file)
        str_cookies = os.environ.get('JIHT_COOKIES')
        cookies = []
        if str_cookies:
            cookies = json.loads(str_cookies)
        if cookies:
            self.log_in_via_cookies(browser, cookies, url)
            if self.authorization_passed(browser, 1):
                return None
        user_name = os.environ.get('JIHT_LOGIN')
        user_password = os.environ.get('JIHT_PASSWORD')
        if user_name and user_password:
            self.log_in_via_username(browser, url, user_name, user_password)
        else:
            return None
        if self.authorization_passed(browser, 1):
            cookies = browser.get_cookies()
            cookies_for_log_in = [
                c for c in cookies if c.get('name') in 
                ['BITRIX_SM_UIDL', 'BITRIX_SM_UIDH']

            ]
            str_cookies = json.dumps(cookies_for_log_in)
            data = {
                'JIHT_LOGIN': user_name,
                'JIHT_PASSWORD': user_password,
                'JIHT_COOKIES': str_cookies
            }
            self.update_dotenv_file(dotenv_file, data)
            return None

    def save_find_element(
        self,
        webelement: webdriver.remote.webelement.WebElement,
        by: str,
        template: str
    ) -> Optional[webdriver.remote.webelement.WebElement]:
    # Change save to safe
        try:
            return webelement.find_element(by, template)
        except NoSuchElementException as e:
            first_part_of_error = e.msg.split(';')[0]
            logging.debug('Cannot find webelement: %s', first_part_of_error)
            # logging.error('Cannot find webelement: %s', first_part_of_error)
            return None

    def log_in_via_username(self, browser, url, user_name, user_password) -> None:
        browser.get(url)
        logging.info('Trying to log in as username `%s`.', user_name)
        auth_link = browser.find_element(By.CSS_SELECTOR, '.auth-links > a')
        auth_link.click()
        login_input = browser.find_element(By.NAME, 'USER_LOGIN')
        password_input = browser.find_element(By.NAME, 'USER_PASSWORD')
        button_enter = browser.find_element(By.NAME, 'Login')
        login_input.send_keys(user_name)
        password_input.send_keys(user_password)
        button_enter.click()
        

    def log_in_via_cookies(self, browser, cookies: List[dict], url: str) -> None:
        browser.get(url)
        browser.delete_all_cookies()
        for c in cookies:
            browser.add_cookie(c)
        browser.get(url)
       
    # def export_cookies(self, cookies: dict, filename: str) -> None:
    #     try:
    #         with open(filename, 'w') as f:
    #             json.dump(cookies, f, indent=4)
    #         logging.info('Cookies have been saved at %s.', filename)
    #     except IOError:
    #         logging.error(
    #             'Cannot create file. Check file name: %s',
    #             filename
    #         )

    # def import_cookies(self, filename: str) -> dict:
    #     cookies = {}
    #     try:
    #         with open(filename, 'r') as f:
    #             cookies = json.load(f)
    #         logging.info('Cookies have been read from %s', filename)
    #     except IOError:
    #         logging.info('Unable to find file: %s.')
    #     return cookies

    def parse_person_properties(self, properties: webdriver.remote.webelement.WebElement) -> dict:
        splited_props = properties.text.splitlines()
        result = {}
        other = []
        hyperlinks = []
        for p in splited_props:
            col_index = p.find(':')
            if col_index == -1:
                other.append(p)
            else:
                key = p[:col_index]
                value = p[col_index+1:]
                result[key] = value.strip()
        hrefs = properties.find_elements(By.TAG_NAME, 'a')
        for h in hrefs:
            hyperlinks.append(h.get_attribute('href'))
        if other:
            result['other'] = other
        if hyperlinks:
            result['hyperlinks'] = hyperlinks
        return result

    def parse_person(self, person: webdriver.remote.webelement.WebElement) -> dict:
        # !Image url should be change from 
        # 'https://jiht.ru/upload/resize_cache/main/67e/100_100_1/image_name.JPG'
        # to 
        # 'https://jiht.ru/upload/main/67e/image_name.JPG'
        name = self.save_find_element(person, By.CLASS_NAME, 'bx-user-name')
        if name:
            name = name.text
        position = self.save_find_element(person, By.CLASS_NAME, 'bx-user-post')
        if position:
            position = position.text
        result = {'ФИО': name, 'Должность': position}
        properties = self.save_find_element(person, By.CLASS_NAME, 'bx-user-properties')
        if properties:
            props = self.parse_person_properties(properties)
            result.update(props)
        image = self.save_find_element(person, By.TAG_NAME, 'img')
        if image:
            result['image_url'] = image.get_attribute('src')
        # result['outerHTML'] = person.get_attribute('outerHTML')
        return result

    def parse_page(self, browser, url: str) -> List[webdriver.remote.webelement.WebElement]:
        logging.info('Start parsing page: `%s`.', url)
        browser.get(url)
        users_on_page = browser.find_elements(By.CLASS_NAME, 'bx-user-info')
        parsed_users = [self.parse_person(user) for user in users_on_page]
        logging.info('Finish parsing page: `%s`.', url)
        return parsed_users

    def parse_pages(self, browser, urls: List[str]) -> dict:
        employees = []
        for url in urls:
            employees.extend(self.parse_page(browser, url))
        return employees

    def get_department_pages(self, browser, url: str) -> List[str]:
        browser.get(url)
        nav = self.save_find_element(browser, By.CLASS_NAME, 'bx-users-nav')
        if nav:
            a_tags = nav.find_elements(By.TAG_NAME, 'a')
            if a_tags:
                last_page_url = a_tags[-1].get_attribute('href')
                ind = last_page_url.rfind('=')
                last_page_number = int(last_page_url[ind+1:])
                return [f'{last_page_url[:ind+1]}{i}'for i in range(1, last_page_number+1)]
            return [url]
        return []

    def export_staff(self, staff: List[dict], filename: str) -> None:
        try:
            logging.info('Start exporting staff.')
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(staff, f, ensure_ascii=False, indent=4)
            logging.info(f'Staff are saved at {filename}.')
        except IOError as err:
            print(err)

    def get_staff(self, url: str) -> List[dict]:
        staff_parser = StaffParser()
        browser = staff_parser.create_browser()
        self.log_in(browser, '.env', url)
        urls = self.get_department_pages(browser, url)
        staff = self.parse_pages(browser, urls)
        self.export_staff(staff, 'staff.json')
        browser.close()
        return staff
        # self.parse_page(browser, url)

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

    def compare_cookies(self, filename1, filename2):
        cookies1 = self.import_cookies(filename1)
        cookies2 = self.import_cookies(filename2)
        cookies = cookies1 + cookies2
        print(len(cookies1), len(cookies2), len(cookies))
        cookies1_names = {el['name']: el['value'] for el in cookies1}
        for i, el in enumerate(sorted(cookies2, key=lambda d: d['name'])):
            if el['name'] in cookies1_names:
                val_1 = cookies1_names[el['name']]
                val_2 = el['value']
                print(i+1, el['name'], ':', val_2, val_1, val_2 == val_1)
            else:
                print(i+1, el['name'], ':', el['value'])


def test():


    # URL = 'https://jiht.ru/'
    URL = 'https://jiht.ru/staff/structure.php?set_filter_structure=Y&structure_UF_DEPARTMENT=1&filter=Y&set_filter=Y&PAGEN_1=2'
    staff_parser = StaffParser()
    staff_parser.get_staff(URL)
    # browser = staff_parser.create_browser()
    # staff_parser.log_in(browser, '.env', URL)
    # staff_parser.log_in(browser, '.env_without_cookies', URL)
    # cookies = staff_parser.import_cookies('./old/cookies_with_auth.json')
    # cookies = staff_parser.import_cookies('cookies_with_login.json')
    # staff_parser.log_in_via_cookies(browser, cookies, URL)
    # staff_parser.compare_cookies('cookies_without_login.json', 'cookies_with_login.json')
    # staff_parser.compare_cookies('./old/cookies_with_auth.json', 'cookies_with_login.json')
    # staff_parser.create_browser()
    # staff_parser.str_cookies()
    # staff_parser.get_staff(URL)

if __name__ == '__main__':
    test()

