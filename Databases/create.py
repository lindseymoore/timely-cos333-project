"""
Sets up the postgres database on Heroku using SQLalchemy and the database.py module.
Currently adds sample data for user dlipman to postgres database.
"""

import os
from os import path
import sys

from flask_sqlalchemy import SQLAlchemy
from psycopg2 import connect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import (AssignmentDetails, Assignments, AssignmentTime, Base,
                      Class, User)


def main(argv):

    if len(argv) != 1:
        print("Usage: python create.py", file=sys.stderr)
        sys.exit(1)
    
    os.environ["DATABASE_URL"] = "postgres://tqclexflqotinz:17a7f4f87e6f11bac2e3de43af17523e0a76790ca79fe0c60e4034b60a8fba45@ec2-54-146-142-58.compute-1.amazonaws.com:5432/dav63a46097qlc"
    DATABASE_URL = os.environ["DATABASE_URL"]
    conn = connect(DATABASE_URL, sslmode='require')

    Session = sessionmaker()
    engine = create_engine(DATABASE_URL)
    Session.configure(bind=engine)
    session = Session()

    Base.metadata.create_all(engine)

    # INSERT SAMPLE DATA FOR USER dlipman INTO DATABASE

    # Add User
    user = User(username="dlipman", password="timelyiscool", school="Princeton University", email="dlipman@princeton.edu")
    session.add(user)
    session.commit()

    # Add Class
    class1 = Class(class_id = 8321, class_title = "COS 333", version = "F2020", active_status = True)
    session.add(class1)
    session.commit()

    # Add Assignment
    assignment = Assignments(assignment_id = 3, assignment_title = "Assignment 3", version = "F2020", class_id = 8321)
    session.add(assignment)
    session.commit()

    # Add AssignmentDetails
    assignment_details = AssignmentDetails(assignment_id = 3, username = "dlipman", class_id = 8321, priority = 2, 
        link = "https://www.cs.princeton.edu/courses/archive/fall20/cos333/asgts/03registrarweb/index.html", due_date = "2020-10-18",
        due_time = "11:00 PM EST", notes= "finished!")
    session.add(assignment_details)
    session.commit()

    # Add AssignmentTime
    assignment_time = AssignmentTime(assignment_id = 3, class_id = 8321, username = "dlipman", estimated_time = 6.0, actual_time = 4.0)
    session.add(assignment_time)
    session.commit()

#-----------------------------------------------------------------------
   
if __name__ == '__main__':
    main(argv)
