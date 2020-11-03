"""
Database class using SQLAlchemy. Contains the tables Tasks, TaskTime
User, TaskDetails, and Class.
"""

from sqlalchemy import Boolean, Column, Date, Float, Integer, String, Time

from timely import db

# Make task_id autoincrementing, class_id no longer primary key in Task, write helper function
# to fetch task_id from title (in db_queries, for use in form_handler)

class Task(db.Model):
    """
    Tasks class represents the Task table:

    ...

    Attributes (columns):
    ---------------------
    username: str
        Username for a given user, retrieved from CAS authentication
    task_id: int
        ID of a given task in a given class with class_id
    class_id: int
        Globally unique class_id given to each class
    title: str
        The literal title of a given task
    repeat: Boolean
        True if task is repeating, False otherwise
    repeat_freq: String
        The frequency at which an task is repeated (i.e. weekly, biweekly, monthly, etc.)
    repeat_end: Date
        Due Date of last occurrence of the repeated task
     """
    __tablename__ = "task"
    username = Column(String, primary_key=True)
    task_id = Column(Integer, primary_key=True, autoincrement=True)
    class_id = Column(Integer)
    title = Column(String)
    repeat = Column(Boolean)
    repeat_freq = Column(String)
    repeat_end = Column(Date)


class TaskIteration(db.Model):
    """
    TaskIteration class represents the task_iteration table:

    ...

    Attributes (columns):
    ---------------------
    username: str
        Username for a given user, retrieved from CAS authentication
    task_id: int
        ID of a given task in a given class with class_id
    class_id: int
        Globally unique class_id given to each class
    iteration: int
        Iteration of a given task (if repeating - i.e., Weekly Reading 3 will have iteration=3).
        If not repeating, iteration = 1. 
    priority: int
        The user"s prioritization of an task, has values {0, 1, 2}
    completed: Boolean
        True if task has been completed already, False otherwise
    link: str
        The url for the task with task_id, class_id
    due_date: Date
        The due date for the task with task_id, class_id
    due_time: Time
        The time the task with task_id, class_id is due on due_date
    notes: str
        Any additional notes about a given task
    est_time: float
        The amount of time a user estimates the task with task_id and class_id will take
    timely_pred: float
        Timely"s predicted amount of time that the task will take
    actual_time: float
        The amount of time it actually took to complete task with task_id and class_id
     """
    __tablename__ = "task_iteration"
    username = Column(String, primary_key = True)
    task_id = Column(Integer, primary_key = True)
    iteration = Column(Integer, primary_key = True)
    class_id = Column(Integer)
    priority = Column(Integer)
    completed = Column(Boolean)
    link = Column(String) 
    due_date = Column(Date)
    due_time = Column(Time)
    notes = Column(String)
    est_time = Column(Float)
    timely_pred = Column(Float)
    actual_time = Column(Float)

class User(db.Model):
    """
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
        The user"s email address
     """
    __tablename__ = "user"
    username = Column(String, primary_key=True)
    password = Column(String)
    school = Column(String)
    email = Column(String)

class Class(db.Model):
    """
    Class class represents the class table:

    ...

    Attributes (columns):
    ---------------------
    class_id: int
        Globally unique class_id given to each class
    title: str
        The literal title of the course
    dept: str
        The department the class is in
    num: int
        The class"s course number
    username: str
        Username for a given user, retrieved from CAS authentication
    active_status: str
        True if class_id is currently being taken, False otherwise
    color: str
        The color of the given course in the UI
     """
    __tablename__ = "class"
    class_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, primary_key=True)
    title = Column(String)
    dept = Column(String)
    num = Column(Integer)
    active_status = Column(Boolean)
    color = Column(String)
