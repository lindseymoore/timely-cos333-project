"""Functions to fetch class and task information."""

from datetime import datetime
from typing import List

from sqlalchemy import desc, func

from timely import db
from timely.models import Class, Task, TaskIteration


def fetch_class_list(username: str) -> List[dict]:
    """
    Given a user with username, query the database to search for all classes the user is enrolled
    in. Return a list of dictionaries, with each dictionary representing one class
    Fetches title, dept, num, and color
    """
    classes = []

    # JOIN query to get information from Class table
    class_details = db.session.query(Class).filter(Class.username == username).all()
    for course in class_details:
        # Create class_obj dictionary with all columns that will be displayed to the user
        class_obj = {"class_id": course.class_id, "title": course.title, "dept": course.dept,
                    "num": course.num, "color": course.color}
        classes.append(class_obj)

    return classes


def fetch_task_list(username: str) -> List[dict]:
    """
    Given a user with username, query the database to search for all tasks the user has
    inputted. Return a list of dictionaries, with each dictionary representing one task.
    Fetches title, priority, est_time, link, notes, due_date, repeat_freq,
    and repeat_end.
    """
    task_list = []

    # JOIN query to get information from task, Class, and TaskIteration tables
    task_info = db.session.query(Task, Class, TaskIteration
                ).filter(Task.username == username
                ).join(TaskIteration, (TaskIteration.task_id == Task.task_id) 
                & (TaskIteration.username == Task.username)
                ).join(Class, Class.class_id == Task.class_id).all()
    for (task, course, task_iteration) in task_info:
        repeat_freq = None
        repeat_end = None

        # If the task is repeating, make an additional query to find it's repeat_freq and repeat_end
        if task.repeat:
            repeat_freq = task.repeat_freq
            repeat_end = task.repeat_end

        # Create task_obj dictionary with all columns that will be displayed to the user
        task_obj = {'title': task.title, 'class': course.title,
                    'priority:': task_iteration.priority,
                    'est_time': task_iteration.est_time,
                    'link': task_iteration.link, 'notes': task_iteration.notes,
                    'due_date': task_iteration.due_date.strftime("%m/%d/%Y"),
                    'repeat_freq': repeat_freq, 'repeat_end': repeat_end,
                    'iteration': task_iteration.iteration, 'color': course.color}

        task_list.append(task_obj)

    return task_list


def fetch_task_details(task_id: int, username: str):
    """
    Given a user with username and task with task_id, query the database to search for the details
    of the class the user has clicked on. Return a dictionary representing the details of one task.
    Fetches title, class, repeat, iteration, priority, link, due_date, notes, est_time.
    """
    task_details_obj = {}

    details = db.session.query(Task, TaskIteration).filter((Task.username == username) &
            (Task.task_id == task_id)).join(TaskIteration, (TaskIteration.username == Task.username)
            & (TaskIteration.task_id == Task.task_id)).all()

    for (task, task_iteration) in details:
        task_details_obj = {"title": task.title, "class": get_class_title(task.class_id),
                    "repeating": task.repeat, "iteration": task_iteration.iteration,
                    "priority": task_iteration.priority, "link": task_iteration.link,
                    "due_date": task_iteration.due_date.strftime("%m/%d/%Y"), 
                    "notes": task_iteration.notes, "est_time": task_iteration.est_time}

    return task_details_obj


def mark_task_complete(task_id: int, username: str):
    """Update the task given by task_id as complete in the db."""
    task = db.session.query(Task).filter((Task.username == username) & (Task.task_id == task_id)).first()
    task.completed = True
    db.session.commit()


def get_class_id(class_title: str) -> int:
    """
    Returns class_id for a given class_title, where class_id is autoincrementing
    """
    class_info = db.session.query(Class).filter(Class.title == class_title).first()
    return class_info.class_id


def get_class_title(class_id: int) -> str:
    """
    Return class_title for a given class_id
    """
    class_info = db.session.query(Class).filter(Class.class_id == class_id).first()
    return class_info.title


def get_task_id(task_title: str, class_id: int) -> int:
    """
    Return task_id for a given task_title and class_id, where task_id is autoincrementing
    """
    task_info = db.session.query(Task).filter((Task.class_id == class_id) &
                (Task.title == task_title)).first()
    return task_info.task_id


def get_next_task_iteration(task_id: int) -> int:
    """
    Returns the next sequential iteration for a given task if it is repeating.
    This is because iterations update sequentially within each repeating assignment.
    This function should be used when adding new tasks into the database.
    """
    # If a repeating assignment already has details,
    # get the next iteration value of the repeating assignment
    iteration = db.session.query(TaskIteration).filter((
        TaskIteration.task_id == task_id)).order_by(desc(TaskIteration.iteration)).first()
    if iteration is None:
        return 1

    return iteration.iteration+1
      
def delete_class(class_id: int):
    """Delete a class and all associated tasks."""
    db.session.query(Class).filter(Class.class_id == class_id).delete()
    db.session.query(Task).filter(Task.class_id == class_id).delete()
    db.session.query(TaskIteration).filter(TaskIteration.class_id == class_id).delete()
    db.session.commit()
    
def delete_task(task_id: int):
    """Delete a task and all associated instances."""
    db.session.query(Task).filter(Task.task_id == task_id).delete()
    db.session.query(TaskIteration).filter(TaskIteration.task_id == task_id).delete()
    db.session.commit()
