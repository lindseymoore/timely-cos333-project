from typing import List

from timely import db
from timely.models import (Task, TaskDetails, TaskTime,
                           Class, ClassDetails, RepeatingTask)


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
        dept = course.class_title[:3]
        num = course.class_title[-3:]
        # Create class_obj dictionary with all columns that will be displayed to the user
        class_obj = {'dept': dept, 'num': num, 'color': course_details.color}
        classes.append(class_obj)

    return classes

def fetch_task_list(username: str) -> List[dict]:
    """ 
    Given a user with username, query the database to search for all tasks the user has inputted. 
    Returns a list of dictionaries, with each dictionary representing one task.
    Fetches task_title, class_title, priority, estimated_time, link, notes, due_date, repeat_freq, and repeat_end. 
    """
    task_list = []

    # JOIN query to get information from task, Class, taskDetails, and taskTime tables
    task_info = db.session.query(Task, Class, TaskDetails, TaskTime,
                      ).filter(Task.username == username
                      ).join(TaskDetails, (TaskDetails.class_id == Task.class_id) 
                      & (TaskDetails.task_id == Task.task_id) & (TaskDetails.username == Task.username)
                      ).join(TaskTime, (TaskTime.class_id == Task.class_id) 
                      & (TaskTime.task_id == Task.task_id) & (TaskTime.username == Task.username)
                      ).join(Class, Class.class_id == Task.class_id).all()
    for (task, course, task_details, task_time) in task_info:
        repeat_freq = None
        repeat_end = None
        
        # If the task is repeating, make an additional query to find it's repeat_freqand repeat_end
        if task.repeat == True:
            repeating_task = db.session.query(RepeatingTask).filter((RepeatingTask.task_id == task.task_id
                                   ) & (RepeatingTask.class_id == task.class_id
                                   ) & (RepeatingTask.username == task.username)).first()
            repeat_freq = repeating_task.repeat_freq
            repeat_end = repeating_task.repeat_end

        # Create task_obj dictionary with all columns that will be displayed to the user
        task_obj = {'task_title': task.task_title, 'class': course.class_title,
                          'priority:': task_details.priority, 'estimated_time': task_time.estimated_time,
                          'link': task_details.link, 'notes': task_details.notes, 'due_date': task_details.due_date,
                          'repeat_freq': repeat_freq, 'repeat_ends': repeat_end}
        task_list.append(task_obj)

    return task_list
