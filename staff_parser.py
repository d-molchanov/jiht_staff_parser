import os
import logging
from dotenv import load_dotenv

logging.basicConfig(
    format='%(asctime)s %(levelname)s:\t%(message)s',
    level=logging.INFO
)

class StaffParser:

    def __init__(self):
        load_dotenv(os.path.abspath('.env'))


def test():
    staff_parser = StaffParser()
    logging.info(os.environ.get('JIHT_LOGIN'))


if __name__ == '__main__':
    test()