"""Functions to process user input and insert as new entries in the database."""

from timely import db
from timely.db_queries import (get_next_task_iteration, get_task_id)
from timely.models import Class, Task, TaskIteration


# Handler function to deal with the creation of classes for input into "class" table
def class_handler(class_iteration: dict):
    """
    Takes class_iteration dictionary (user inputted fields in new class form) as input.
    Configures this dictionary into Class classes and inputs them as new entires in the class table.
    """

    new_class = Class(username = class_iteration["username"], title = class_iteration["title"],
                dept = class_iteration["dept"], num = class_iteration["num"],
                active_status = True, color = class_iteration["color"])

    db.session.add(new_class)
    db.session.commit()


# Handles the creation of tasks for input into "Task" table
def task_handler(details: dict):
    """
    Takes details dictionary (user inputted fields in new Task form) as input.
    Configures this dictionary into Task and TaskIteration
    classes and inputs them as new entries into the task and task_iteration
   tables respectively.
    """
    task = Task()
    task_iteration = TaskIteration()

    # Insert into task table
    task.username = details["username"]
    task.class_id = details["class_id"]
    task.title = details["task_title"]
    if details["repeat_freq"] != "":
        task.repeat = True
        task.repeat_freq = details["repeat_freq"]
        if details["repeat_end"] != "":
            task.repeat_end = details["repeat_end"]
        else:
            task.repeat_end = None
    else:
        task.repeat = False

    db.session.add(task)
    db.session.commit()

    # Get task_id for inserted task, as task_id is autoincrementing.
    # Get iteration of task with task_id.
    task_id = get_task_id(details['task_title'], details['class_id'])
    iteration = get_next_task_iteration(task_id)

    # Insert into TaskIteration table
    task_iteration.username = details["username"]
    task_iteration.task_id = task_id
    task_iteration.class_id = details['class_id']
    task_iteration.iteration = iteration
    task_iteration.priority = details["priority"]
    task_iteration.link = details["link"]
    task_iteration.due_date = details["due_date"]
    task_iteration.due_time = details["due_time"]

    task_iteration.notes = details["notes"]
    task_iteration.completed = False

    # Insert times into TaskIteration table
    task_iteration.est_time = details["est_time"]
    task_iteration.actual_time = None
    task_iteration.timely_pred = details["est_time"]

    db.session.add(task_iteration)
    db.session.commit()


def update_task_details(task_details: dict):
    """Updates a task's details based on form input."""
    username = task_details['username']
    task_id = task_details['task_id']

    task, task_iteration = db.session.query(Task, TaskIteration).filter( \
                (Task.username == username) &
                (Task.task_id == task_id)).join(TaskIteration, \
                (TaskIteration.username == Task.username) & \
                (TaskIteration.task_id == Task.task_id)).first()

    task.title = task_details['title']

    # TODO If going from repeating to non-repeating, need to remove future iterations?
    task.repeat = task_details['repeat']
    if task_details['repeat']:
        task.repeat_freq = task_details['repeat_freq']
        task.repeat_end = task_details['repeat_end']

    task_iteration.iteration = task_details['iteration']
    task_iteration.priority = task_details['priority']
    task_iteration.link = task_details['link']
    task_iteration.due_date = task_details['due_date']
    task_iteration.due_time = task_details['due_time']
    task_iteration.notes = task_details['notes']
    task_iteration.est_time = task_details['est_time']

    db.session.commit()
    