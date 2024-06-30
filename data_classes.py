from dataclasses import dataclass, asdict
import json
from typing import Optional, List, Dict

# @dataclass
# class DCEmployee:
#     full_name: str
#     position: str
#     email: list
#     work_phone: list 
#     department: list
#     building: list
#     office: list
#     internal_phone: list
#     title: str
#     degree: str
#     image_url: str
#     notes: list

@dataclass
class DCDepartment:
    department_name: str
    department_page: Optional[str] = None

@dataclass
class DCBuilding:
    building_name: Optional[str] = None
    building_address: Optional[str] = None

@dataclass
class DCOffice:
    office_number: Optional[str] = None
    department_id: Optional[int] = None
    building_id: Optional[int] = None


def test():
    d1 = DCDepartment(department_name='1', department_page='1')
    print(d1)
    d2 = DCDepartment(department_name='2', department_page=2)
    print(d2)
    d3 = DCDepartment(**{'department_name': 3})
    print(d3)
    s = json.dumps(asdict(d3))
    print(s)
if __name__ == '__main__':
    test()