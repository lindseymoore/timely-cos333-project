from typing import List

from timely import db
from timely.models import (Assignment, AssignmentDetails, AssignmentTime,
                           Class, ClassDetails, RepeatingAssignment)


def fetch_class_list(username: str) -> List[dict]:
    """ 
    Given a user with username, query the database to search for all classes the user is enrolled in. 
    Returns a list of dictionaries, with each dictionary representing one class 
    Fetches class_dept, class_num, and color 
    """
    classes = [] 

    # JOIN query to get information from Class and ClassDetails tables
    class_details = db.session.query(Class, ClassDetails).join(ClassDetails, ClassDetails.class_id == Class.class_id).all()
    for course, course_details in class_details:
        # Gets course department and number from the class_title
        class_dept = course.class_title[:3]
        class_num = course.class_title[-3:]
        # Create class_obj dictionary with all columns that will be displayed to the user
        class_obj = {'class_dept': class_dept, 'class_num': class_num, 'color': course_details.color}
        classes.append(class_obj)

    return classes

def fetch_assignment_list(username: str) -> List[dict]:
    """ 
    Given a user with username, query the database to search for all assignments the user has inputted. 
    Returns a list of dictionaries, with each dictionary representing one assignment.
    Fetches assignment_title, class_title, priority, estimated_time, link, notes, due_date, repeat_freq, and repeat_end. 
    """
    assignment_list = []

    # JOIN query to get information from Assignment, Class, AssignmentDetails, and AssignmentTime tables
    assignment_info = db.session.query(Assignment, Class, AssignmentDetails, AssignmentTime,
                      ).filter(Assignment.username == username
                      ).join(AssignmentDetails, (AssignmentDetails.class_id == Assignment.class_id) 
                      & (AssignmentDetails.assignment_id == Assignment.assignment_id) & (AssignmentDetails.username == Assignment.username)
                      ).join(AssignmentTime, (AssignmentTime.class_id == Assignment.class_id) 
                      & (AssignmentTime.assignment_id == Assignment.assignment_id) & (AssignmentTime.username == Assignment.username)
                      ).join(Class, Class.class_id == Assignment.class_id).all()
    for (assignment, course, assignment_details, assignment_time) in assignment_info:
        repeat_freq = None
        repeat_end = None
        
        # If the assignment is repeating, make an additional query to find it's repeat_freqand repeat_end
        if assignment.repeat == True:
            repeating_assignment = db.session.query(RepeatingAssignment).filter((RepeatingAssignment.assignment_id == Assignment.assignment_id
                                   ) & (RepeatingAssignment.class_id == Assignment.class_id
                                   ) & (RepeatingAssignment.username == Assignment.username)).first()
            repeat_freq = repeating_assignment.repeat_freq
            repeat_end = repeating_assignment.repeat_end

        # Create assignment_obj dictionary with all columns that will be displayed to the user
        assignment_obj = {'assignment_title': assignment.assignment_title, 'class': course.class_title,
                          'priority:': assignment_details.priority, 'estimated_time': assignment_time.estimated_time,
                          'link': assignment_details.link, 'notes': assignment_details.notes, 'due_date': assignment_details.due_date,
                          'repeat_freq': repeat_freq, 'repeat_ends': repeat_end}
        assignment_list.append(assignment_obj)

    return assignment_list
