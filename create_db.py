"""
Set up the postgres database on Heroku using SQLalchemy and the database.py module.
Currently adds sample data for user dlipman to postgres database.
"""

import os
import sys

from psycopg2 import connect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from timely.models import (AssignmentDetails, Assignments, AssignmentTime,
                           Class, User)
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

    db.create_all(engine)

    # INSERT SAMPLE DATA FOR USER dlipman INTO DATABASE

    # Add User
    user = User(username="dlipman", password="timelyiscool",
                school="Princeton University", email="dlipman@princeton.edu")
    session.add(user)
    session.commit()

    # Add Class
    class1 = Class(class_id=8321, class_title="COS 333",
                version="F2020", active_status=True)
    session.add(class1)
    session.commit()

    # Add Assignment
    assignment = Assignments(assignment_id=3, assignment_title="Assignment 3",
                version="F2020", class_id=8321)
    session.add(assignment)
    session.commit()

    # Add AssignmentDetails
    assignment_details = AssignmentDetails(assignment_id=3,
                username="dlipman", class_id=8321, priority=2,
                link="https://www.cs.princeton.edu/courses/archive/\
                    fall20/cos333/asgts/03registrarweb/index.html",
                due_date="2020-10-18", due_time="11:00 PM EST", notes="finished!")
    session.add(assignment_details)
    session.commit()

    # Add AssignmentTime
    assignment_time = AssignmentTime(assignment_id=3, class_id=8321,
                username="dlipman", estimated_time=6.0, actual_time=4.0)
    session.add(assignment_time)
    session.commit()

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main(sys.argv)
