import json
from typing import List, Dict
import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)s:\t%(message)s',
    level=logging.INFO
)

class StaffProcessor:

    def import_staff(self, filename: str) -> List[Dict[str, str]]:
        staff = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                staff = json.load(f)
            logging.info('Persons were read from %s.', filename)
        except IOError:
            logging.error('Unable to find %s.', filename)
        return staff

    def process_staff(self, staff: List[Dict[str, str]]) -> None:
        multiple_emails = []
        multiple_phones = []
        additional_phones = []
        others = []
        fields = []
        for person in staff:
            e_mail = person.get('E-Mail')
            if e_mail:
                if e_mail.count('@') > 1:
                    multiple_emails.append(person)
            phone_number = person.get('Рабочий')
            if phone_number:
                if ',' in phone_number:
                    multiple_phones.append(person)
                if 'д' in phone_number:
                    additional_phones.append(person)
                    print(phone_number)

            other = person.get('other')
            if other:
                others.append(person)
            for key in person.keys():
                if key not in fields:
                    fields.append(key)
                if key == 'ICQ':
                    print(person)

        print(f'Multiple phones: {len(multiple_phones)}')
        print(f'Multiple emails: {len(multiple_emails)}')
        print(f'Others: {len(others)}')
        print(f'Additional phones: {len(additional_phones)}')

        print(fields)

def test() -> None:
    staff_processor = StaffProcessor()
    staff = staff_processor.import_staff('staff.json')
    staff_processor.process_staff(staff)

if __name__ == '__main__':
    test()