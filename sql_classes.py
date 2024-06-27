from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Date
from sqlalchemy import ForeignKey

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship

from sqlalchemy.types import BINARY

class Base(DeclarativeBase): pass

class Employee(Base):
    __tablename__ = 'employees'

    employee_id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String)
    position = Column(String)
    degree = Column(String)
    title = Column(String)
    image_url = Column(String)
    note = Column(String)
    emails = relationship('Email', back_populates='employee', cascade='all, delete-orphan')
    work_phones = relationship('WorkPhone', back_populates='employee', cascade='all, delete-orphan')
    internal_phones = relationship('InternalPhone', back_populates='employee', cascade='all, delete-orphan')


    def __str__(self):
        return f'class Employee: {self.full_name}'


class Department(Base):
    __tablename__ = 'departments'

    department_id = Column(Integer, primary_key=True, autoincrement=True)
    department_name = Column(String)
    department_page = Column(String)
    # offices = relationship('Office', back_populates='department', cascade='all, delete-orphan')


class Building(Base):
    __tablename__ = 'buildings'

    building_id = Column(Integer, primary_key=True, autoincrement=True)
    building_name = Column(String)
    building_address = Column(String)
    offices = relationship('Office', back_populates='building', cascade='all, delete-orphan')


class Office(Base):
    __tablename__ = 'offices'

    office_id = Column(Integer, primary_key=True, autoincrement=True)
    office_number = Column(String)
    department_id = Column(Integer, ForeignKey('departments.department_id'))
    building_id = Column(Integer, ForeignKey('buildings.building_id'))
    # department = relationship('Department', back_populates='offices', cascade='all')
    building = relationship('Building', back_populates='offices', cascade='all')


class WorkPhone(Base):
    __tablename__= 'work_phones'

    work_phone_id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(String)
    employee_id = Column(Integer, ForeignKey('employees.employee_id'))
    employee = relationship('Employee', back_populates='work_phones', cascade='all')


class InternalPhone(Base):
    __tablename__= 'internal_phones'


    internal_phone_id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(String)
    employee_id = Column(Integer, ForeignKey('employees.employee_id'))
    employee = relationship('Employee', back_populates='internal_phones', cascade='all')


class Email(Base):
    __tablename__  = 'emails'

    email_id = Column(Integer, primary_key=True, autoincrement=True)
    email_address = Column(String)
    employee_id = Column(Integer, ForeignKey('employees.employee_id'))
    employee = relationship('Employee', back_populates='emails', cascade='all')


