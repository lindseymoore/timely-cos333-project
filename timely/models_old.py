"""
Database class using SQLAlchemy. Contains the tables Assignments, AssignmentTime
User, AssignmentDetails, and Class.
"""

from sqlalchemy import Boolean, Column, Date, Float, Integer, String, Time
from sqlalchemy.ext.declarative import declarative_base

from timely import db

Base = declarative_base()

# TODO Should we create globally unique assignment_ids
# or should we delegate assignment_ids within each class?

class Assignments(db.Model):
    '''
    Assignments class represents the assignment table:

    ...

    Attributes (columns):
    ---------------------
    assignment_id: int
        ID of a given assignment in a given class with class_id
    assignment_title: str
        The literal title of a given assignment
    version: str
        Either "F<YEAR> or S<YEAR>", representing iteration of a given class
    class_id: int
        Globally unique class_id given to each class
     '''
    __tablename__ = 'assignments'
    username = Column()
    assignment_id = Column(Integer, primary_key=True)
    assignment_title = Column(String)
    class_id = Column(Integer, primary_key=True)

class AssignmentTime(db.Model):
    '''
    AssignmentTime class represents the time table:

    ...

    Attributes (columns):
    ---------------------
    assignment_id: int
        ID of a given assignment in a given class with class_id
    class_id: int
        Globally unique class_id given to each class
    username: str
        Username for a given user, retrieved from CAS authentication
    estimated_time: float
        The amount of time a user estimates the assignment with assignment_id and class_id will take
    actual_time: float
        The amount of time it actually took to complete assignment with assignment_id and class_id
     '''
    __tablename__ = 'time'
    assignment_id = Column(Integer, primary_key=True)
    class_id = Column(Integer, primary_key=True)
    username = Column(String, primary_key=True)
    estimated_time = Column(Float)
    timely_prediction = Column(Float)
    actual_time = Column(Float)

class User(db.Model):
    '''
    User class represents the user table:

    ...

    Attributes (columns):
    ---------------------
    username: str
        Username for a given user, retrieved from CAS authentication
    password: str
        Password for user with username, retrived from CAS authentication
        TODO: Password encryption?
    school: str
        School/University the user attends (in our case Princeton)
    email: str
        The user's email address
     '''
    __tablename__ = 'user'
    username = Column(String, primary_key=True)
    password = Column(String)
    school = Column(String)
    email = Column(String)

class AssignmentDetails(db.Model):
    '''
    AssignmentDetails class represents the assignment_details table:

    ...

    Attributes (columns):
    ---------------------
    assignment_id: int
        ID of a given assignment in a given class with class_id
    username: str
        Username for a given user, retrieved from CAS authentication
    class_id: int
        Globally unique class_id given to each class
    priority: int
        The user's prioritization of an assignment, has values {0, 1, 2}
    link: str
        The url for the assignment with assignment_id, class_id
    due_date: Date
        The due date for the assignment with assignment_id, class_id
    due_time: Time
        The time the assignment with assignment_id, class_id is due on due_date
    repeat_freq: String
        The frequency at which an assignment is repeated (i.e. every week, biweekly, every month, etc.)
    repeat_end: Date
        Due Date of last occurence of the repeated assignment
    notes: str
        Any additional notes about a given assignment
     '''
    __tablename__ = 'assignment_details'
    assignment_id = Column(Integer, primary_key=True)
    username = Column(String, primary_key=True)
    class_id = Column(Integer, primary_key=True)
    priority = Column(Integer)
    link = Column(String) 
    due_date = Column(Date)
    due_time = Column(Time)
    repeat = Column(Boolean)
    repeat_freq = Column(String)
    repeat_ends = Column(Date)
    iteration_number = 
    notes = Column(String)

class Class(db.Model):
    '''
    Class class represents the class table:

    ...

    Attributes (columns):
    ---------------------
    class_id: int
        Globally unique class_id given to each class
    class_title: str
        The literal title of the class with a given class_id
    version: str
        Either "F<YEAR> or S<YEAR>", representing iteration of a given class
    active_status: str
        True if class_id is currently being taken, False otherwise
     '''
    __tablename__ = 'class'
    class_id = Column(Integer, primary_key=True)
    class_title = Column(String)
    version = Column(String, primary_key=True)
    active_status = Column(Boolean)
    color = Column(String)
