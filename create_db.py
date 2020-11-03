"""
Set up the postgres database on Heroku using SQLalchemy and the database.py module.
Currently adds sample data for user dlipman to postgres database.
"""

import os
import sys

from timely.db_queries import get_class_id, get_task_id
from psycopg2 import connect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from timely import db
from timely.db_queries import get_class_id
from timely.models import (Class, Task, TaskIteration, User)


def main(argv):
    """Create the postgres database."""
    if len(argv) != 1:
        print("Usage: python create_db.py", file=sys.stderr)
        sys.exit(1)

    database_url = os.environ["DATABASE_URL"]
    connect(database_url, sslmode="require")

    make_session = sessionmaker()
    engine = create_engine(database_url)
    make_session.configure(bind=engine)

    db.create_all()

    # INSERT SAMPLE DATA FOR USER dlipman INTO DATABASE

    # Add User
    user = User(username="princeton_student", password="timelyiscool",
                school="Princeton University", email="dlipman@princeton.edu")
    db.session.add(user)
    db.session.commit()

    # Add Class 8321, 9362, 8004, 8080
    class1 = Class(username = "princeton_student", title="Advanced Programming Techniques",
                dept = "COS", num = "333", active_status = True, color="red")
    class2 = Class(username = "princeton_student", title="Intro to Machine Learning",
                dept = "COS", num = "324", active_status = True, color="purple")
   
    db.session.add(class1)
    db.session.add(class2)
    db.session.commit()

    # Add task
    task_333 = Task(username="princeton_student", class_id=get_class_id('Advanced Programming Techniques'), title="task 3",
                repeat=False, repeat_freq="biweekly", repeat_end="2020-12-15")
    task_324 = Task(username="princeton_student", class_id=get_class_id('Intro to Machine Learning'), title="Homework",
                repeat=True, repeat_freq="biweekly", repeat_end="2020-12-15")

    db.session.add(task_333)
    db.session.add(task_324)
    db.session.commit()

    # Get classids and taskids
    class_id_333 = get_class_id('Advanced Programming Techniques')
    class_id_324 = get_class_id('Intro to Machine Learning')

    task_id_333 = get_task_id('task 3', class_id_333)
    task_id_324 = get_task_id('Homework', class_id_324)

    # Add taskDetails
    task333_details = TaskIteration(task_id=task_id_333,
                username="princeton_student", class_id=class_id_333, priority=2, iteration=1, 
                link="https://www.cs.princeton.edu/courses/archive/\
                    fall20/cos333/asgts/03registrarweb/index.html",
                due_date="2020-10-18", due_time="11:00 PM EST", notes="finished!", completed=False, 
                est_time=6.0, actual_time=4.0, timely_pred=None)
    task324_details = TaskIteration(task_id=task_id_324,
                username="princeton_student", class_id=class_id_324, priority=2, iteration=1, 
                link=None,
                due_date="2020-10-20", due_time="11:59 PM EST", notes="finished!", completed=False, 
                est_time=4.0, actual_time=5.0, timely_pred=None)

    db.session.add(task333_details)
    db.session.add(task324_details)
    db.session.commit()

#-----------------------------------------------------------------------

if __name__ == "__main__":
    main(sys.argv)
