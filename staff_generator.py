import random
import json
import logging
from faker import Faker
from typing import List, Dict

class StaffGenerator:

    def generate_employee(self, fake: Faker) -> Dict[str, str]:
        employee = {}
        employee['name'] = fake.name()
        employee['position'] = fake.job()
        labs = [(f'Лаборатория {n}', f'https://domain.com/lab{n}') for n in range(1, 5)]
        random.shuffle(labs)
        employee['lab'] = {lab[0]: lab[1] for lab in labs[:random.randint(1,3)]}
        employee['email'] = [fake.ascii_free_email() for _ in range(random.randint(1, 4))]
        employee['work_phone'] = [fake.phone_number() for _ in range(random.randint(1, 3))]
        employee['internal_phone'] = [f'0{random.randint(100, 200)}' for _ in range(random.randint(1, 3))]
        buildings = [f'К{i}' for i in range(1,11)]
        random.shuffle(buildings)
        # employee['building'] = [building for building in buildings[:random.randint(1, 3)]]
        employee['building'] = [building for building in buildings[:1]]
        employee['office'] =[
            f'{random.randint(1,2)}{random.randint(0,2)}{random.randint(0,10)}'
        ]
        return employee

    def generate(self, amount: int) -> List[Dict[str, str]]:
        fake = Faker('ru_Ru')
        return [self.generate_employee(fake) for _ in range(amount)]

    def export_json(self, data, filename: str) -> None:
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logging.info('Data were written to `%s`.', filename)
        except IOError:
            logging.error('Unable to create `%s`.', filename)
    


def test() -> None:
    staff_generator = StaffGenerator()
    staff = staff_generator.generate(1000)
    staff_generator.export_json(staff, 'syntetic_staff.json')
    # print(*staff, sep='\n')

if __name__ == '__main__':
    test()