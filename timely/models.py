"""
Database class using SQLAlchemy. Contains the tables Assignments, AssignmentTime
User, AssignmentDetails, and Class.
"""

from sqlalchemy import Boolean, Column, Date, Float, Integer, String, Time
from sqlalchemy.ext.declarative import declarative_base

from timely import db

# TODO Should we create globally unique assignment_ids
# or should we delegate assignment_ids within each class?


class Assignment(db.Model):
    '''
    Assignments class represents the assignment table:

    ...

    Attributes (columns):
    ---------------------
    username: str
        Username for a given user, retrieved from CAS authentication
    assignment_id: int
        ID of a given assignment in a given class with class_id
    class_id: int
        Globally unique class_id given to each class
    assignment_title: str
        The literal title of a given assignment
    repeat: Boolean
        True if assignment is repeating, False otherwise
    completed: Boolean
        True if assignment has been completed already, False otherwise
     '''
    __tablename__ = 'assignment'
    username = Column(String, primary_key = True)
    assignment_id = Column(Integer, primary_key=True)
    class_id = Column(Integer, primary_key=True)
    assignment_title = Column(String)
    repeat = Column(Boolean)
    completed = Column(Boolean)


class AssignmentDetails(db.Model):
    '''
    AssignmentDetails class represents the assignment_details table:

    ...

    Attributes (columns):
    ---------------------
    username: str
        Username for a given user, retrieved from CAS authentication
    assignment_id: int
        ID of a given assignment in a given class with class_id
    class_id: int
        Globally unique class_id given to each class
    assignment_iteration: int
        Iteration of a given assignment (if repeating - i.e., Weekly Reading 3 will have assignment_iteration=3). If not repeating, assignment_iteration = 1. 
    priority: int
        The user's prioritization of an assignment, has values {0, 1, 2}
    link: str
        The url for the assignment with assignment_id, class_id
    due_date: Date
        The due date for the assignment with assignment_id, class_id
    due_time: Time
        The time the assignment with assignment_id, class_id is due on due_date
    notes: str
        Any additional notes about a given assignment
     '''
    __tablename__ = 'assignment_details'
    username = Column(String, primary_key = True)
    assignment_id = Column(Integer, primary_key = True)
    class_id = Column(Integer, primary_key = True)
    assignment_iteration = Column(Integer, primary_key = True)
    priority = Column(Integer)
    link = Column(String) 
    due_date = Column(Date)
    due_time = Column(Time)
    notes = Column(String)


class RepeatingAssignment(db.Model):
    '''
    RepeatingAssignment class represents the repeating_assignment table:

    ...

    Attributes (columns):
    ---------------------
    username: str
        Username for a given user, retrieved from CAS authentication
    assignment_id: int
        ID of a given assignment in a given class with class_id
    class_id: int
        Globally unique class_id given to each class
    repeat_freq: String
        The frequency at which an assignment is repeated (i.e. weekly, biweekly, monthly, etc.)
    repeat_end: Date
        Due Date of last occurence of the repeated assignment
     '''
    __tablename__ = 'repeating_assignment'
    username = Column(String, primary_key = True)
    assignment_id = Column(Integer, primary_key=True)
    class_id = Column(Integer, primary_key=True)
    repeat_freq = Column(String)
    repeat_end = Column(Date)


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
    assignment_iteration: int
        Iteration of a given assignment (if repeating). If not repeating, assignment_iteration = 1.
    estimated_time: float
        The amount of time a user estimates the assignment with assignment_id and class_id will take
    timely_prediction: float
        Timely's predicted amount of time that the assignment will take
    actual_time: float
        The amount of time it actually took to complete assignment with assignment_id and class_id
     '''
    __tablename__ = 'time'
    assignment_id = Column(Integer, primary_key=True)
    class_id = Column(Integer, primary_key=True)
    username = Column(String, primary_key=True)
    assignment_iteration = Column(String, primary_key = True)
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

class Class(db.Model):
    '''
    Class class represents the class table:

    ...

    Attributes (columns):
    ---------------------
    class_id: int
        Globally unique class_id given to each class
    class_title: str
        The department/number title of the course (i.e. COS333)
     '''
    __tablename__ = 'class'
    class_id = Column(Integer, primary_key=True)
    class_title = Column(String)


class ClassDetails(db.Model):
    '''
    Class class represents the class_details table:

    ...

    Attributes (columns):
    ---------------------
    class_id: int
        Globally unique class_id given to each class
    username: str
        Username for a given user, retrieved from CAS authentication
    active_status: str
        True if class_id is currently being taken, False otherwise
    color: str
        The color a course will be di
     '''
    __tablename__ = 'class_details'
    class_id = Column(Integer, primary_key=True)
    username = Column(String, primary_key=True)
    active_status = Column(Boolean)
    color = Column(String)
    # grade = Column(String)
