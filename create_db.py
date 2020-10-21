"""
Set up the postgres database on Heroku using SQLalchemy and the database.py module.
Currently adds sample data for user dlipman to postgres database.
"""

import os
import sys

from psycopg2 import connect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from timely.models import (AssignmentDetails, Assignment, AssignmentTime,
                           Class, ClassDetails, RepeatingAssignment, User)
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
    class1 = Class(class_id=8321, class_title="COS333")
    class1_details = ClassDetails(class_id=8321, username="dlipman", active_status=True, color="Blue")
    class2 = Class(class_id=9362, class_title="COS324")
    class2_details = ClassDetails(class_id=9362, username="dlipman", active_status=True, color="Red")
    class3 = Class(class_id=8004, class_title="COS316")
    class3_details = ClassDetails(class_id=8004, username="dlipman", active_status=True, color="Green")
    class4 = Class(class_id=8080, class_title="CEE102")
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

    # Add Assignment
    assignment_333 = Assignment(username="dlipman", assignment_id=3, class_id=8321, assignment_title="Assignment 3",
                repeat=False, completed=True)
    assignment_324 = Assignment(username="dlipman", assignment_id=4, class_id=9362, assignment_title="Homework",
                repeat=True, completed=True)
    assignment_316 = Assignment(username="dlipman", assignment_id=4, class_id=8004, assignment_title="Programming Assignment",
                repeat=True, completed=False)
    assignment_102 = Assignment(username="dlipman", assignment_id=5, class_id=8080, assignment_title="Homework",
                repeat=False, completed=False)
    db.session.add(assignment_333)
    db.session.add(assignment_324)
    db.session.add(assignment_316)
    db.session.add(assignment_102)
    db.session.commit()

    # Add AssignmentDetails
    assignment333_details = AssignmentDetails(assignment_id=3,
                username="dlipman", class_id=8321, priority=2, assignment_iteration=1, 
                link="https://www.cs.princeton.edu/courses/archive/\
                    fall20/cos333/asgts/03registrarweb/index.html",
                due_date="2020-10-18", due_time="11:00 PM EST", notes="finished!")
    assignment324_details = AssignmentDetails(assignment_id=4,
                username="dlipman", class_id=9362, priority=2, assignment_iteration=4, 
                link=None,
                due_date="2020-10-20", due_time="11:59 PM EST", notes="finished!")
    assignment316_details = AssignmentDetails(assignment_id=4,
                username="dlipman", class_id=8004, priority=2, assignment_iteration=4, 
                link="https://github.com/cos316/assignment4-thefridge4",
                due_date="2020-10-28", due_time="11:59 PM EST", notes="working over the weekend")
    assignment102_details = AssignmentDetails(assignment_id=5,
                username="dlipman", class_id=8080, priority=1, assignment_iteration=1, 
                link=None,
                due_date="2020-10-28", due_time="11:59 PM EST", notes="working over the weekend, watch lectures first")
    db.session.add(assignment333_details)
    db.session.add(assignment324_details)
    db.session.add(assignment316_details)
    db.session.add(assignment102_details)
    db.session.commit()

    # Add RepeatingAssignment
    assignment324_rep = RepeatingAssignment(username="dlipman", assignment_id=4, class_id=9362, repeat_freq="biweekly", repeat_end="2020-12-15")
    assignment316_rep = RepeatingAssignment(username="dlipman", assignment_id=4, class_id=8004, repeat_freq="biweekly", repeat_end="2020-12-15")
    db.session.add(assignment324_rep)
    db.session.add(assignment316_rep)
    db.session.commit()

    # Add AssignmentTime
    assignment333_time = AssignmentTime(assignment_id=3, class_id=8321,
                username="dlipman", assignment_iteration=1, estimated_time=6.0, actual_time=4.0, timely_prediction=None)
    assignment324_time = AssignmentTime(assignment_id=4, class_id=9362,
                username="dlipman", assignment_iteration=4, estimated_time=4.0, actual_time=5.0, timely_prediction=None)
    assignment316_time = AssignmentTime(assignment_id=4, class_id=8004,
                username="dlipman", assignment_iteration=4, estimated_time=6.0, actual_time=None, timely_prediction=None)
    assignment102_time = AssignmentTime(assignment_id=5, class_id=8080,
                username="dlipman", assignment_iteration=1, estimated_time=2.0, actual_time=None, timely_prediction=None)
    db.session.add(assignment333_time)
    db.session.add(assignment324_time)
    db.session.add(assignment316_time)
    db.session.add(assignment102_time)
    db.session.commit()

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main(sys.argv)
