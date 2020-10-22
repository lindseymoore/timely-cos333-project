"""
Set up the postgres database on Heroku using SQLalchemy and the database.py module.
Currently adds sample data for user dlipman to postgres database.
"""

import os
import sys

from psycopg2 import connect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from timely import db
from timely.models import (Class, ClassDetails, RepeatingTask, Task,
                           TaskDetails, TaskTime, User)
from db_queries import get_class_id


def main(argv):
    """Create the postgres database."""
    if len(argv) != 1:
        print("Usage: python create_db.py", file=sys.stderr)
        sys.exit(1)

    database_url = os.environ["DATABASE_URL"]
    connect(database_url, sslmode='require')

    make_session = sessionmaker()
    engine = create_engine(database_url)
    make_session.configure(bind=engine)
    session = make_session()

    db.create_all()

    # INSERT SAMPLE DATA FOR USER dlipman INTO DATABASE

    # Add User
    user = User(username="dlipman", password="timelyiscool",
                school="Princeton University", email="dlipman@princeton.edu")
    db.session.add(user)
    db.session.commit()

    # Add Class 8321, 9362, 8004, 8080
    class1 = Class(title="COS333")
    class2 = Class(title="COS324")
    class3 = Class(title="COS316")
    class4 = Class(title="CEE102")
    db.session.add(class1)
    db.session.add(class2)
    db.session.add(class3)
    db.session.add(class4)
    db.session.commit()

    class1_details = ClassDetails(username="dlipman", class_id=get_class_id('COS333'), active_status=True, color="Blue")
    class2_details = ClassDetails(username="dlipman", class_id=get_class_id('COS324'), active_status=True, color="Red")
    class3_details = ClassDetails(username="dlipman", class_id=get_class_id('COS316'), active_status=True, color="Green")
    class4_details = ClassDetails(username="dlipman", class_id=get_class_id('CEE102'), active_status=True, color="Purple")

    db.session.add(class1_details)
    db.session.add(class2_details)
    db.session.add(class3_details)
    db.session.add(class4_details)
    db.session.commit()

    # Add task
    task_333 = Task(username="dlipman", task_id=3, class_id=get_class_id('COS333'), title="task 3",
                repeat=False, completed=True)
    task_324 = Task(username="dlipman", task_id=4, class_id=get_class_id('COS324'), title="Homework",
                repeat=True, completed=True)
    task_316 = Task(username="dlipman", task_id=4, class_id=get_class_id('COS316'), title="Programming task",
                repeat=True, completed=False)
    task_102 = Task(username="dlipman", task_id=5, class_id=get_class_id('CEE102'), title="Homework",
                repeat=False, completed=False)
    db.session.add(task_333)
    db.session.add(task_324)
    db.session.add(task_316)
    db.session.add(task_102)
    db.session.commit()

    # Add taskDetails
    task333_details = TaskDetails(task_id=3,
                username="dlipman", class_id=get_class_id('COS333'), priority=2, iteration=1, 
                link="https://www.cs.princeton.edu/courses/archive/\
                    fall20/cos333/asgts/03registrarweb/index.html",
                due_date="2020-10-18", due_time="11:00 PM EST", notes="finished!")
    task324_details = TaskDetails(task_id=4,
                username="dlipman", class_id=get_class_id('COS324'), priority=2, iteration=4, 
                link=None,
                due_date="2020-10-20", due_time="11:59 PM EST", notes="finished!")
    task316_details = TaskDetails(task_id=4,
                username="dlipman", class_id=get_class_id('COS316'), priority=2, iteration=4, 
                link="https://github.com/cos316/task4-thefridge4",
                due_date="2020-10-28", due_time="11:59 PM EST", notes="working over the weekend")
    task102_details = TaskDetails(task_id=5,
                username="dlipman", class_id=get_class_id('CEE102'), priority=1, iteration=1, 
                link=None,
                due_date="2020-10-28", due_time="11:59 PM EST", notes="working over the weekend, watch lectures first")
    db.session.add(task333_details)
    db.session.add(task324_details)
    db.session.add(task316_details)
    db.session.add(task102_details)
    db.session.commit()

    # Add Repeatingtask
    task324_rep = RepeatingTask(username="dlipman", task_id=4, class_id=get_class_id('COS324'), repeat_freq="biweekly", repeat_end="2020-12-15")
    task316_rep = RepeatingTask(username="dlipman", task_id=4, class_id=get_class_id('COS316'), repeat_freq="biweekly", repeat_end="2020-12-15")
    db.session.add(task324_rep)
    db.session.add(task316_rep)
    db.session.commit()

    # Add TaskTime
    task333_time = TaskTime(task_id=3, class_id=get_class_id('COS333'),
                username="dlipman", iteration=1, est_time=6.0, actual_time=4.0, timely_pred=None)
    task324_time = TaskTime(task_id=4, class_id=get_class_id('COS324'),
                username="dlipman", iteration=4, est_time=4.0, actual_time=5.0, timely_pred=None)
    task316_time = TaskTime(task_id=4, class_id=get_class_id('COS316'),
                username="dlipman", iteration=4, est_time=6.0, actual_time=None, timely_pred=None)
    task102_time = TaskTime(task_id=5, class_id=get_class_id('CEE102'),
                username="dlipman", iteration=1, est_time=2.0, actual_time=None, timely_pred=None)
    db.session.add(task333_time)
    db.session.add(task324_time)
    db.session.add(task316_time)
    db.session.add(task102_time)
    db.session.commit()

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main(sys.argv)
