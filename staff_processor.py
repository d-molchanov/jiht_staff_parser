import json
from typing import List, Dict
import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)s:\t%(message)s',
    level=logging.INFO
)

class StaffProcessor:

    def import_staff(self, filename: str) -> List[Dict[str, str]]:
        # 'ФИО', 'Должность', 'E-Mail', 'Подразделения', 'hyperlinks',
        # 'Рабочий', 'Корпус', 'Комната', 'Внутренний телефон',
        # 'Ученое звание', 'Ученая степень', 'image_url', 'WWW-страница', 'ICQ'
        staff = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                staff = json.load(f)
            logging.info('Persons were read from %s.', filename)
        except IOError:
            logging.error('Unable to find %s.', filename)
        return staff

    def process_phone_numbers(self, phone_numbers: List[str]) -> str:
        # {';', '-', 'о', ')', '+', ',', 'ф', ' ', 'д', '.', 'б', '('}
        result = set()
        for phone_number in phone_numbers:
            for ch in phone_number:
                if not ch.isdecimal():
                    result.add(ch)
        return result

    def process_additional_number(self, phone_number: str) -> str:
        phone_number = phone_number.replace('-', '')
        phone_number = phone_number.strip()
        phone_number = phone_number.replace(' ', ',')
        phone_number = phone_number.replace('.', '')
        temp = phone_number.split(',')
        temp = [f'0{el}' if len(el) == 3 else el for el in temp]
        if len(temp) > 1:
            return ','.join(temp)
        else:
            return temp[0]



    def extract_phone_numbers(self, staff: List[Dict[str, str]]) -> List[str]:
        phone_numbers = []
        for person in staff:
            phone_number = person.get('Рабочий')
            if phone_number:
                additional_number = ''
                temp = phone_number.split('доб.')
                phone_number = temp[0]
                if len(temp) == 2: additional_number = temp[1]
                phone_number = phone_number.replace('8(', '(')
                phone_number = phone_number.replace('8 (', '(')
                phone_number = phone_number.replace('+7', '')
                phone_number = phone_number.replace('+7 ', '')
                phone_number = phone_number.replace(';', '(')
                # phone_number = phone_number.replace('доб.', '(')
                phone_number = phone_number.replace('ф.', '(')
                phone_number = phone_number.replace('-', '')
                phone_number = phone_number.replace('.', '')
                phone_number = phone_number.replace(',', '(')
                temp = [el.replace(' ', '') for el in phone_number.split('(')]
                temp = [el for el in temp if el]
                temp = [el.replace(')', '') for el in temp]
                # temp = [el.replace(',', '') for el in temp]
                temp = [f'8{el}' if len(el) == 10 else el for el in temp]
                temp = [f'0{el}' if len(el) == 3 else el for el in temp]
                temp_ = []
                for el in temp:
                    if len(el) == 4:
                        if additional_number:
                            additional_number = f'{additional_number},{el}'
                        else:
                            additional_number = el
                    elif len(el) == 7:
                        temp_.append(f'8495{el}')
                    elif len(el) == 8:
                        # Этот выбор сделан из-за ошибки на сайте, вообще нужно построить
                        # базу данных на основе информации о подразделениях, искать там 
                        # сотрудников схожих подразделений и подставлять телефоны и коды городов.
                        temp_.append(f'8{el[:3]}45{el[3:]}')
                    else:
                        temp_.append(el)
                temp = temp_
                    # if 4 < len(el) < 10: print(el, person.get('Рабочий'), person.get('Внутренний телефон'), sep=' $ ')
                phone_number = ' , '.join(temp)
                if additional_number:
                    additional_number = self.process_additional_number(additional_number)
                    phone_number = f'{phone_number}: {additional_number}'
                # phone_number = phone_number.replace(' ,', ',')
                # if '496' in phone_number: print(phone_number, person.get('Внутренний телефон'), sep='=')
                # phone_number = phone_number.replace(' ', '')
                # phone_number = phone_number.split(',')
                # for p in phone_number:
                #     p.split('доб.')
                # if len(p) 
                # if len(phone_number) == 1: phone_number = phone_number[0]
                phone_numbers.append(phone_number)
        print(self.process_phone_numbers(phone_numbers))
        return phone_numbers

    def export_json(self, data, filename: str) -> None:
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logging.info('Data were written to `%s`.', filename)
        except IOError:
            logging.error('Unable to create `%s`.', filename)

    def process_staff(self, staff: List[Dict[str, str]]) -> None:
        multiple_emails = []
        multiple_phones = []
        additional_phones = []
        others = []
        fields = []
        non_decimal_chars = set()
        for person in staff:
            e_mail = person.get('E-Mail')
            if e_mail:
                if e_mail.count('@') > 1:
                    multiple_emails.append(person)
            phone_number = person.get('Рабочий')
            if phone_number:
                # non_decimal_chars.update(self.process_phone_number(phone_number))
                if ',' in phone_number:
                    multiple_phones.append(person)
                if 'ф' in phone_number:
                    # additional_phones.append(person)
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
        print(non_decimal_chars)
        print(fields)

def test() -> None:
    staff_processor = StaffProcessor()
    staff = staff_processor.import_staff('staff.json')
    phone_numbers = staff_processor.extract_phone_numbers(staff)
    staff_processor.export_json(phone_numbers, 'phones.json')
    # staff_processor.process_staff(staff)

if __name__ == '__main__':
    test()