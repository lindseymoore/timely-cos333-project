import models
from timely import db
from timely.models import (Assignment, AssignmentDetails, AssignmentTime, Class,
                           RepeatingAssignment)


def fetchClassList(username: str):
    new_class = Class.query.filter_by(username == username).all()

    return new_class

def fetchAssignmentList(username: str):
    assignment_list = []

    assignment = db.session.query(Assignment, Class, AssignmentDetails, AssignmentTime, RepeatingAssignment,
    ).filter(Assignment.username == username).filter(AssignmentDetails.username == Assignment.username
    ).filter(RepeatingAssignment.username == Assignment.username).filter(AssignmentTime.username == Assignment.username
    ).filter(Class.class_id == Assignment.class_id).all()

    return assignment