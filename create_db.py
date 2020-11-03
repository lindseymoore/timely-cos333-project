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
from timely.models import (Class, RepeatingTask, Task, TaskDetails, TaskTime,
                           User)


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
    # class3 = Class(username = "dlipman", title="Principles of Computer System Design",
    #             dept = "COS", num = "316", active_status = True, color="orange")
    # class4 = Class(username = "dlipman", title="History of Engineering",
    #             dept = "CEE", num = "102", active_status = True, color="green")
    db.session.add(class1)
    db.session.add(class2)
    # db.session.add(class3)
    # db.session.add(class4)
    db.session.commit()

    # Add task
    task_333 = Task(username="princeton_student", class_id=get_class_id('Advanced Programming Techniques'), title="task 3",
                repeat=False, completed=False)
    task_324 = Task(username="princeton_student", class_id=get_class_id('Intro to Machine Learning'), title="Homework",
                repeat=True, completed=False)
    # task_316 = Task(username="dlipman", class_id=get_class_id('Principles of Computer System Design'), title="Programming task",
    #             repeat=True, completed=False)
    # task_102 = Task(username="dlipman", class_id=get_class_id('History of Engineering'), title="Homework",
    #             repeat=False, completed=False)
    db.session.add(task_333)
    db.session.add(task_324)
    # db.session.add(task_316)
    # db.session.add(task_102)
    db.session.commit()

    # Get classids and taskids
    class_id_333 = get_class_id('Advanced Programming Techniques')
    class_id_324 = get_class_id('Intro to Machine Learning')
    # class_id_316 = get_class_id('Principles of Computer System Design')
    # class_id_102 = get_class_id('History of Engineering')

    task_id_333 = get_task_id('task 3', class_id_333)
    task_id_324 = get_task_id('Homework', class_id_324)
    # task_id_316 = get_task_id('Programming task', class_id_316)
    # task_id_102 = get_task_id('Homework', class_id_102)

    # Add taskDetails
    task333_details = TaskDetails(task_id=task_id_333,
                username="princeton_student", class_id=class_id_333, priority=2, iteration=1, 
                link="https://www.cs.princeton.edu/courses/archive/\
                    fall20/cos333/asgts/03registrarweb/index.html",
                due_date="2020-10-18", due_time="11:00 PM EST", notes="finished!")
    task324_details = TaskDetails(task_id=task_id_324,
                username="princeton_student", class_id=class_id_324, priority=2, iteration=4, 
                link=None,
                due_date="2020-10-20", due_time="11:59 PM EST", notes="finished!")
    # task316_details = TaskDetails(task_id=task_id_316,
    #             username="dlipman", class_id=class_id_316, priority=2, iteration=4, 
    #             link="https://github.com/cos316/task4-thefridge4",
    #             due_date="2020-10-28", due_time="11:59 PM EST", notes="working over the weekend")
    # task102_details = TaskDetails(task_id=task_id_102,
    #             username="dlipman", class_id=class_id_102, priority=1, iteration=1, 
    #             link=None,
    #             due_date="2020-10-28", due_time="11:59 PM EST", notes="working over the weekend, watch lectures first")
    db.session.add(task333_details)
    db.session.add(task324_details)
    # db.session.add(task316_details)
    # db.session.add(task102_details)
    db.session.commit()

    # Add Repeatingtask
    task324_rep = RepeatingTask(username="princeton_student", task_id=task_id_324, class_id=class_id_324, repeat_freq="biweekly", repeat_end="2020-12-15")
    #task316_rep = RepeatingTask(username="dlipman", task_id=task_id_316, class_id=class_id_316, repeat_freq="biweekly", repeat_end="2020-12-15")
    db.session.add(task324_rep)
    #db.session.add(task316_rep)
    db.session.commit()

    # Add TaskTime
    task333_time = TaskTime(task_id=task_id_333, class_id=class_id_333,
                username="princeton_student", iteration=1, est_time=6.0, actual_time=4.0, timely_pred=None)
    task324_time = TaskTime(task_id=task_id_324, class_id=class_id_324,
                username="princeton_student", iteration=4, est_time=4.0, actual_time=5.0, timely_pred=None)
    # task316_time = TaskTime(task_id=task_id_316, class_id=class_id_316,
    #             username="dlipman", iteration=4, est_time=6.0, actual_time=None, timely_pred=None)
    # task102_time = TaskTime(task_id=task_id_102, class_id=class_id_102,
    #             username="dlipman", iteration=1, est_time=2.0, actual_time=None, timely_pred=None)
    db.session.add(task333_time)
    db.session.add(task324_time)
    # db.session.add(task316_time)
    # db.session.add(task102_time)
    db.session.commit()

#-----------------------------------------------------------------------

if __name__ == "__main__":
    main(sys.argv)
