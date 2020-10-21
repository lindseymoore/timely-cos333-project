"""
Set up the postgres database on Heroku using SQLalchemy and the database.py module.
Currently adds sample data for user dlipman to postgres database.
"""

import os
import sys

from psycopg2 import connect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from timely.models import (taskDetails, task, taskTime,
                           Class, ClassDetails, Repeatingtask, User)
from timely import db


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

    # Add Class
    class1 = Class(title="COS333")
    class1_details = ClassDetails(class_id=8321, username="dlipman", active_status=True, color="Blue")
    class2 = Class(title="COS324")
    class2_details = ClassDetails(class_id=9362, username="dlipman", active_status=True, color="Red")
    class3 = Class(title="COS316")
    class3_details = ClassDetails(class_id=8004, username="dlipman", active_status=True, color="Green")
    class4 = Class(title="CEE102")
    class4_details = ClassDetails(class_id=8080, username="dlipman", active_status=True, color="Purple")
    
    db.session.add(class1)
    db.session.add(class2)
    db.session.add(class3)
    db.session.add(class4)
    db.session.add(class1_details)
    db.session.add(class2_details)
    db.session.add(class3_details)
    db.session.add(class4_details)
    db.session.commit()

    # Add task
    task_333 = task(username="dlipman", task_id=3, class_id=8321, task_title="task 3",
                repeat=False, completed=True)
    task_324 = task(username="dlipman", task_id=4, class_id=9362, task_title="Homework",
                repeat=True, completed=True)
    task_316 = task(username="dlipman", task_id=4, class_id=8004, task_title="Programming task",
                repeat=True, completed=False)
    task_102 = task(username="dlipman", task_id=5, class_id=8080, task_title="Homework",
                repeat=False, completed=False)
    db.session.add(task_333)
    db.session.add(task_324)
    db.session.add(task_316)
    db.session.add(task_102)
    db.session.commit()

    # Add taskDetails
    task333_details = taskDetails(task_id=3,
                username="dlipman", class_id=8321, priority=2, task_iteration=1, 
                link="https://www.cs.princeton.edu/courses/archive/\
                    fall20/cos333/asgts/03registrarweb/index.html",
                due_date="2020-10-18", due_time="11:00 PM EST", notes="finished!")
    task324_details = taskDetails(task_id=4,
                username="dlipman", class_id=9362, priority=2, task_iteration=4, 
                link=None,
                due_date="2020-10-20", due_time="11:59 PM EST", notes="finished!")
    task316_details = taskDetails(task_id=4,
                username="dlipman", class_id=8004, priority=2, task_iteration=4, 
                link="https://github.com/cos316/task4-thefridge4",
                due_date="2020-10-28", due_time="11:59 PM EST", notes="working over the weekend")
    task102_details = taskDetails(task_id=5,
                username="dlipman", class_id=8080, priority=1, task_iteration=1, 
                link=None,
                due_date="2020-10-28", due_time="11:59 PM EST", notes="working over the weekend, watch lectures first")
    db.session.add(task333_details)
    db.session.add(task324_details)
    db.session.add(task316_details)
    db.session.add(task102_details)
    db.session.commit()

    # Add Repeatingtask
    task324_rep = Repeatingtask(username="dlipman", task_id=4, class_id=9362, repeat_freq="biweekly", repeat_end="2020-12-15")
    task316_rep = Repeatingtask(username="dlipman", task_id=4, class_id=8004, repeat_freq="biweekly", repeat_end="2020-12-15")
    db.session.add(task324_rep)
    db.session.add(task316_rep)
    db.session.commit()

    # Add taskTime
    task333_time = taskTime(task_id=3, class_id=8321,
                username="dlipman", task_iteration=1, estimated_time=6.0, actual_time=4.0, timely_prediction=None)
    task324_time = taskTime(task_id=4, class_id=9362,
                username="dlipman", task_iteration=4, estimated_time=4.0, actual_time=5.0, timely_prediction=None)
    task316_time = taskTime(task_id=4, class_id=8004,
                username="dlipman", task_iteration=4, estimated_time=6.0, actual_time=None, timely_prediction=None)
    task102_time = taskTime(task_id=5, class_id=8080,
                username="dlipman", task_iteration=1, estimated_time=2.0, actual_time=None, timely_prediction=None)
    db.session.add(task333_time)
    db.session.add(task324_time)
    db.session.add(task316_time)
    db.session.add(task102_time)
    db.session.commit()

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main(sys.argv)
