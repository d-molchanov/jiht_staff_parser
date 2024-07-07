from dataclasses import dataclass, asdict, field
import json
from typing import Optional, List, Dict

@dataclass
class DCEmployee:
    full_name: Optional[str] = None
    department: List[str] = field(default_factory=list)
    position: Optional[str] = None
    degree: Optional[str] = None
    title: Optional[str] = None
    image_url: Optional[str] = None
    email: Optional[str] = None
    work_phone: List[str] = field(default_factory=list) 
    internal_phone: List[str] = field(default_factory=list)
    building: Optional[str] = None
    office: List[str] = field(default_factory=list)
    notes: Optional[str] = None

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
    e1 = DCEmployee(full_name='Иванов Иван', email='example@domain.com')
    print(e1)
if __name__ == '__main__':
    test()