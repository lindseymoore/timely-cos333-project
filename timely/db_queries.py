"""Functions to fetch class and task information."""

from typing import List

from sqlalchemy import func

from timely import db
from timely.models import (Class, RepeatingTask, Task,
                           TaskDetails, TaskTime)


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

        # If the task is repeating, make an additional query to find it"s repeat_freqand repeat_end
        if task.repeat:
            repeating_task = db.session.query(RepeatingTask).filter((
                        RepeatingTask.task_id == task.task_id
                        ) & (RepeatingTask.class_id == task.class_id
                        ) & (RepeatingTask.username == task.username)).first()
            repeat_freq = repeating_task.repeat_freq
            repeat_end = repeating_task.repeat_end

        # Create task_obj dictionary with all columns that will be displayed to the user
        task_obj = {"title": task.title, "class": course.title, "task_id": task.task_id,
                    "color": course.color,
                    "priority:": task_details.priority,
                    "completed": task.completed,
                    "est_time": task_time.est_time,
                    "link": task_details.link, "notes": task_details.notes,
                    "due_date": task_details.due_date,
                    "repeat_freq": repeat_freq, "repeat_ends": repeat_end}

        task_list.append(task_obj)

    return task_list

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


def get_task_id(task_title: str, class_id: int) -> int:
    """
    Return task_id for a given task_title and class_id, where task_id is autoincrementing
    """
    task_info = db.session.query(Task).filter((Task.class_id == class_id) &
                (Task.title == task_title)).first()
    return task_info.task_id


def get_next_task_iteration(class_id: int, task_id: int) -> int:
    """
    Returns the next sequential iteration for a given task if it is repeating.
    This is because iterations update sequentially within each repeating assignment.
    This function should be used when adding new tasks into the database.
    """
    try:
        # If a repeating assignment already has details,
        # get the next iteration value of the repeating assignment
        iteration = db.session.query(func.max(TaskDetails.iteration)).filter((
                    TaskDetails.class_id == class_id
                    ) & (TaskDetails.task_id == task_id)).first()
        return iteration.iteration+1
    except:
        # If there is no entry yet for the task in TaskDetails, its iteration is 1
        return 1


def delete_class(class_id: int):
    """Delete a class and all associated tasks."""
    db.session.query(Class).filter(Class.class_id == class_id).delete()
    db.session.query(Task).filter(Task.class_id == class_id).delete()
    db.session.query(TaskDetails).filter(TaskDetails.class_id == class_id).delete()
    db.session.query(RepeatingTask).filter(RepeatingTask.class_id == class_id).delete()
    db.session.query(TaskTime).filter(TaskTime.class_id == class_id).delete()
    db.session.commit()

def delete_task(task_id: int):
    """Delete a task and all associated instances."""
    db.session.query(Task).filter(Task.task_id == task_id).delete()
    db.session.query(TaskDetails).filter(TaskDetails.task_id == task_id).delete()
    db.session.query(RepeatingTask).filter(RepeatingTask.task_id == task_id).delete()
    db.session.query(TaskTime).filter(TaskTime.task_id == task_id).delete()
    db.session.commit()
