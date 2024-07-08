import json
from typing import List, Dict
import logging
from bs4 import BeautifulSoup as bs
from bs4.element import Tag, NavigableString


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

    def process_phone_numbers(self, staff: List[Dict[str, str]]) -> List[Dict[str, str]]:
        # {';', '-', 'о', ')', '+', ',', 'ф', ' ', 'д', '.', 'б', '('}
        result = []
        for person in staff:
            phone_field = person.get('Рабочий')
            internal_field = person.get('Внутренний телефон')
            str_work_phones = ''
            str_internal_phones = ''
            if phone_field:
                phone_numbers = self.process_work_phone_field(phone_field)
                work_phones = phone_numbers.get('work_phones')
                internal_phones = phone_numbers.get('internal_phones')
                if work_phones:
                    str_work_phones = ','.join(work_phones)
                if internal_phones:
                    str_internal_phones = ','.join(internal_phones)
            str_internal_field = ''
            if internal_field:
                str_internal_field = ','.join(self.process_internal_phone_field(internal_field))
            str_result = f'{str_work_phones}: {str_internal_phones}; {str_internal_field}'
            if str_result != ': ; ':
                result.append(str_result)
        return result

    def process_internal_phone_field(self, phone_number: str) -> str:
        phone_number = phone_number.strip()
        phone_number = phone_number.replace('-', '')
        phone_number = phone_number.replace(' ', ',')
        phone_number = phone_number.replace('/', ',')
        phone_number = phone_number.replace('.', '')
        phone_numbers = [phone for phone in phone_number.split(',') if phone.isdecimal()]
        return [f'0{phone}' if len(phone) == 3 else phone for phone in phone_numbers]
        

    def process_work_phone_field(self, phone_field: str) -> List[str]:
        internal_phones = []
        if 'доб.' in phone_field:
            work_phone, internal_phone = phone_field.split('доб.')
            internal_phones = self.process_internal_phone_field(
                internal_phone
            )
        else:
            work_phone = phone_field
        work_phone = work_phone.replace('8(', '(')
        work_phone = work_phone.replace('8 (', '(')
        work_phone = work_phone.replace('+7', '')
        work_phone = work_phone.replace('+7 ', '')
        work_phone = work_phone.replace(';', '(')
        work_phone = work_phone.replace('ф.', '(')
        work_phone = work_phone.replace('-', '')
        work_phone = work_phone.replace('.', '')
        work_phone = work_phone.replace(',', '(')
        work_phone = work_phone.replace(')', '')
        work_phones_ = [
            phone.replace(' ', '') for phone in work_phone.split('(')
        ]
        work_phones_ = [phone for phone in work_phones_ if phone]
        work_phones = []
        for phone in work_phones_:
            if len(phone) == 3:
                internal_phones.append(f'0{phone}')
            elif len(phone) == 4:
                internal_phones.append(phone)
            elif len(phone) == 7:
                work_phones.append(f'8495{phone}')
            elif len(phone) == 8:
                # Этот выбор сделан из-за ошибки на сайте, вообще нужно построить
                # базу данных на основе информации о подразделениях, искать там 
                # сотрудников схожих подразделений и подставлять телефоны и коды городов.
                work_phones.append(f'8{phone[:3]}45{phone[3:]}')
            elif len(phone) == 10:
                work_phones.append(f'8{phone}')
            else:
                work_phones.append(phone)
        result = {}
        if work_phones:
            result['work_phones'] = work_phones
        if internal_phones:
            result['internal_phones'] = internal_phones
        # phone_field = ' , '.join(temp)
        # if additional_number:
        #     additional_number = self.process_internal_phone_field(additional_number)
        #     phone_field = f'{phone_field}: {additional_number}'
        return result

    def process_departments(self, staff: List[Dict[str, str]]) -> List[Dict[str, str]]:
        departments = {}
        for person in staff:
            departments_ = person.get('Подразделения')
            if len(departments_) > 1: print(person)
            building = person.get('Корпус')
            office = person.get('Комната')
            hyperlinks = person.get('hyperlinks')
            # hrefs = [h for h in hyperlinks if h.startswith('https://jiht.ru')]
            for d, v in departments_.items():
                if d in departments:
                    departments[d]['amount'] += 1
                    if f'{building}: {office}' not in departments[d]['office']:
                        departments[d]['office'].append(f'{building}: {office}')
                else:
                    departments[d] = {}
                    departments[d]['href'] = v 
                    departments[d]['amount'] = 1
                    departments[d]['office'] = [f'{building}: {office}']
                    # departments[d]['hrefs'] = []
                # for h in hrefs:
                #     if h not in departments[d]['hrefs']:
                #         departments[d]['hrefs'].append(h)
        for k in sorted(departments.keys()):
            print(f'{k}: {departments[k]["amount"]}')
        print(len(departments))
        print(sum([d['amount'] for d in departments.values()]))
        return departments

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

    def _handle_tag_a(self, web_element: Tag):
        return web_element.text.strip(), web_element['href']
        # return web_element if web_element.name != 'br' else None
            
    def _handle_navigable_string(self, web_element: NavigableString):
        result = web_element.replace('\n', ' ').strip()
        return NavigableString(result) if result and result != ',' else None
    
    def filter_web_elements(self, web_element):
        handlers = {
            'a': self._handle_tag_a,
            'None': self._handle_navigable_string
        }
        handler = handlers.get(str(web_element.name))
        return handler(web_element) if handler else None



    def parse_employee_properties(self, web_element: Tag):
        properties = []
        for el in web_element.children:
            # print(el.name, f'`{el}`')
            property_ = self.filter_web_elements(el)
            if property_:
                properties.append(property_)
                print(type(property_))
        print(*[f'{i}: `{p}`' for i, p in enumerate(properties)], sep='\n')

        return properties

    def _handle_str(self, input_str: str):
        if input_str.strip().endswith(':'):
            return  input_str[:-1]
        return tuple([el.strip() for el in input_str.split(':', 1)])

    def parse_props(self, props):
        result = {}
        for el in props:
            if isinstance(el, str):
                res = self._handle_str(el)
                if isinstance(res, tuple):
                    result[res[0]] = res[1]
                if isinstance(res, str):
                    result[res] = {}
            if isinstance(el, tuple):
                result[res][el[0]] = el[1]
        return result

    def format_employee_information(self, properties: dict):
        substitution = {
            'ФИО': 'full_name',
            'Должность': 'position',
            'E-Mail': 'email',
            'Подразделения': 'department',
            'Рабочий': 'work_phone',
            'Корпус': 'building',
            'Комната': 'office',
            'Внутренний телефон': 'internal_phone',
            'Ученое звание': 'title',
            'Ученая степень': 'degree'#,
            # 'WWW-страница': 'website',
            # 'ICQ': 'icq'
        }
        result = {}
        notes = []
        for k, v in properties.items():
            if k in substitution:
                if isinstance(v, list):
                    if len(v) == 1:
                        v = v[0]
                result[substitution[k]] = v
            else:
                if isinstance(v, list):
                    v = ', '.join(v)
                notes.append(f'{k}: {v}')
        if notes:
            result['notes'] = ';\n'.join(notes)
        return result

    # def parse_employee(self, div: str) -> dict:
    def parse_employee(self, div: Tag) -> dict:
        result = {}
        name = div.find(class_='bx-user-name')
        if name:
            name = name.text.strip()
            result['ФИО'] = name
        position = div.find(class_='bx-user-post')
        if position:
            position = position.text.strip()
            result['Должность'] = position
        properties = div.find(class_='bx-user-properties')
        props = self.parse_employee_properties(properties)
        p = self.parse_props(props)
        result.update(p)
        for k, v in result.items():
            print(f'{k} -> {v}')

            if isinstance(v, dict) and k != 'Подразделения':
                result[k] = list(v.keys())
        result = self.format_employee_information(result)
        image = div.find('img')
        if image:
            result['image_url'] = image['src']
        print(result)
        # Здесь уже нужно возвращать dataclass DCEmployee
        return result

    def reduce_data(self, filename: str) -> None:
        with open(filename, 'r', encoding='utf-8') as f:
            soup = bs(f, 'html.parser')
            divs = soup.find_all('div', class_='bx-user-info')
            # with open('divs.html', 'w') as w:
            #     w.write('\n'.join([d.prettify() for d in divs]))
            print(len(divs))
            staff = [self.parse_employee(div) for div in divs[74:75]]
            # staff = [self.parse_employee(div) for div in divs[78:79]]
            # staff = [self.parse_employee(div) for div in divs]
            for person in staff:
                internal_phone = person.get('internal_phone')
                if internal_phone:
                    person['internal_phone'] = self.process_internal_phone_field(internal_phone)
                work_phone = person.get('work_phone')
                if work_phone:
                    work_phone = self.process_work_phone_field(work_phone)
                    additional_internal_phone = work_phone.get('internal_phones')
                    if additional_internal_phone:
                        if internal_phone:
                            person['internal_phone'].extend(additional_internal_phone)
                        else:
                            person['internal_phone'] = additional_internal_phone
                    work_phone_ = work_phone.get('work_phones')
                    if work_phone_:
                        person['work_phone'] = work_phone_
                building = person.get('building')
                if building:
                    if ',' in building:
                        print(person)
            return staff
                

def test() -> None:
    staff_processor = StaffProcessor()
    staff_1 = staff_processor.import_staff('staff.json')
    staff_2 = staff_processor.reduce_data('divs.html')
    # print(staff_2[75])
    # print(*sorted(list(n)), sep='\n')
    # staff_processor.reduce_data('reduced_divs.html')
    # staff = staff_processor.import_staff('staff.json')
    # # phone_numbers = staff_processor.process_phone_numbers(staff)
    # # staff_processor.export_json(phone_numbers, 'phones.json')
    # departments = staff_processor.process_departments(staff)
    # staff_processor.export_json(dict(sorted(departments.items())), 'departments.json')
    # # staff_processor.process_staff(staff)


if __name__ == '__main__':
    test()