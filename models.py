from datetime import datetime
from datetime import date
from datetime import timedelta
import json
import logging
import sqlite3
from typing import List, Dict
from time import perf_counter

from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import BINARY
from sqlalchemy.engine.base import Engine

from sql_classes import Base
from sql_classes import Employee
from sql_classes import Department
from sql_classes import Email
from sql_classes import WorkPhone
from sql_classes import InternalPhone
from sql_classes import Building
from sql_classes import Office

from data_classes import DCDepartment
from data_classes import DCBuilding
from data_classes import DCOffice


logging.basicConfig(
    format='%(asctime)s %(levelname)s:\t%(message)s',
    level=logging.INFO
)

class DatabaseManager:

    def create_engine_by_dbm(self, db_url: str) -> Engine:
        engine = create_engine(db_url)
        # engine = create_engine(db_url, echo=True)

        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            if isinstance(dbapi_connection, sqlite3.Connection):
               cursor = dbapi_connection.cursor()
               cursor.execute("PRAGMA foreign_keys=ON")
               cursor.close()

        return engine


    def create_tables(self, engine: Engine) -> None:
        Base.metadata.create_all(bind=engine)

    def import_json(self, filename: str) -> List[Dict[str, str]]:
        data = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logging.info('Persons were read from %s.', filename)
        except IOError:
            logging.error('Unable to find %s.', filename)
        return data

    def add_records(self, engine: Engine, employees: List[Dict[str, str]]) -> None:
        with Session(autoflush=False, bind=engine) as db:
            records = []
            email_records = []
            work_phones_records = []
            for entry in employees:
                employee = Employee(
                    full_name=entry.get('name'),
                    position=entry.get('position'),
                    degree=entry.get('degree'),
                    title=entry.get('title'),
                    image_url=entry.get('image_url'),
                    note=entry.get('note')
                )
                records.append(employee)
                emails = entry.get('email')
                for e in emails:
                    email_records.append(
                        Email(
                            email_address=e,
                            employee=employee
                        )
                    )
                work_phones = entry.get('work_phone')
                for p in work_phones:
                    WorkPhone(
                        phone_number=p,
                        employee=employee
                    )
                internal_phones = entry.get('internal_phone')
                for p in internal_phones:
                    InternalPhone(
                        phone_number=p,
                        employee=employee
                    )
            db.add_all(records)
            db.commit()

    def add_staff(self, engine: Engine, staff: List[Dict[str, str]]) -> None:
        with Session(autoflush=False, bind=engine) as db:
            buildings = []
            labs = []
            for entry in staff:
                departments = entry.get('Подразделения')
                for k, v in departments.items():
                    d = DCDepartment(
                        department_name=k,
                        department_page=v
                    )
                    if d not in labs:
                        labs.append(d)
                # offices = entry.get('office')
                building = entry.get('Корпус')
                if building:
                    b = Building(
                        building_name=building[0],
                        building_address=None
                    )
                    if b not in buildings:
                        buildings.append(b)
            config = {'department_name': '1', 'department_page': '2'}
            print(len(labs), len(buildings), Department(**config)==Department(**config))
            db.add_all(labs)
            db.add_all(buildings)
            db.commit()
            # for o in offices:
            #     Office(
            #         office_number=o,
            #     )

    def delete_by_id(self, id: int, sql_class: Base, engine: Engine):
        with Session(autoflush=False, bind=engine) as db:
            entry = db.get(sql_class, id)
            db.delete(entry)
            db.commit()
            logging.info('`%s` was deleted.', entry)


def test() -> None:
    DB_URL = 'sqlite:///test_db.db'
    database_manager = DatabaseManager()
    engine = database_manager.create_engine_by_dbm(DB_URL)
    database_manager.create_tables(engine)
    staff = database_manager.import_json('staff.json')
    # staff = database_manager.import_json('syntetic_staff.json')
    database_manager.add_staff(engine, staff[:10])
    # database_manager.add_records(engine, staff[:10])
    # database_manager.delete_by_id(6, Employee, engine)

if __name__ == '__main__':
    test()