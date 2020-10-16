#!/usr/bin/env python

#-----------------------------------------------------------------------
# database.py
# Authors: David Lipman, Lindsey Moore, Mariah Crawford, Jorge Zreik
#-----------------------------------------------------------------------

from sqlalchemy import Boolean, Column, Date, Float, Integer, String, Time
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# TODO Should we create globally unique assignment_ids or should we delegate assignment_ids within each class?

class Assignments (Base):
    __tablename__ = 'assignments'
    assignment_id = Column(Integer, primary_key=True)
    assignment_title = Column(String)
    version = Column(String, primary_key=True) #Ex: Either F2020 or S2020
    class_id = Column(Integer, primary_key=True)

class AssignmentTime (Base):
    __tablename__ = 'time'
    assignment_id = Column(Integer, primary_key=True)
    class_id = Column(Integer, primary_key=True)
    username = Column(String, primary_key=True)
    estimated_time = Column(Float)
    actual_time = Column(Float)

class User (Base):
    __tablename__ = 'user'
    username = Column(String, primary_key=True)
    password = Column(String)
    school = Column(String)
    email = Column(String)

class AssignmentDetails (Base):
    __tablename__ = 'assignment_details'
    assignment_id = Column(Integer, primary_key=True)
    username = Column(String, primary_key=True)
    class_id = Column(Integer, primary_key=True)
    priority = Column(Integer)
    link = Column(String)
    due_date = Column(Date)
    due_time = Column(Time)
    notes = Column(String)

class Class (Base):
    __tablename__ = 'class'
    class_id = Column(Integer, primary_key=True)
    class_title = Column(String)
    version = Column(String, primary_key=True)
    active_status = Column(Boolean)
