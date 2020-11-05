"""Functions to process user input and insert as new entries in the database."""

from timely import db
from timely.db_queries import (get_class_id, get_next_task_iteration, get_task_id)
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
    task_iteration.timely_prediction = None

    db.session.add(task_iteration)
    db.session.commit()
