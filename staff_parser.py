import os
from typing import List
import logging
from dotenv import load_dotenv, dotenv_values


logging.basicConfig(
    format='%(asctime)s %(levelname)s:\t%(message)s',
    level=logging.DEBUG
)



class StaffParser:

    def __init__(self) -> None:
        self._load_dotenv('./.env')

    def _load_dotenv(self, path_: str) -> None:
        load_dotenv(os.path.abspath(path_))
        logging.debug('dotenv values: %s', dotenv_values())


def test():
    staff_parser = StaffParser()


if __name__ == '__main__':
    test()
