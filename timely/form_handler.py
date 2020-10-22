"""Functions to process user input and insert as new entries in the database."""

from timely.db_queries import get_class_id, get_next_task_id, get_next_task_iteration
from timely import db
from timely.models import (Class, ClassDetails, RepeatingTask, Task,
                           TaskDetails, TaskTime)


# Handler function to deal with the creation of classes for input into "class" table
def class_handler(class_details: dict):
    '''
    Takes class_details dictionary (user inputted fields in new class form) as input.
    Configures this dictionary into Class, and ClassDetails classes and inputs them as
    new entires in the class and class_details tables respectively.
    '''
    new_class = Class(class_title = class_details['class_title'])
    db.session.add(new_class)
    db.session.commit()

    # Insert into class_details table
    details = ClassDetails()
    details.class_id = get_class_id(class_details['class_title'])
    details.username = 'Princeton Student'  # TODO UPDATE TO USE CAS AUTHENTICATION
    details.active_status = True
    details.color = class_details['color']
    db.session.add(details)
    db.session.commit()


# Handles the creation of tasks for input into "Task" table
def task_handler(details: dict):
    '''
    Takes details dictionary (user inputted fields in new Task form) as input.  
    Configures this dictionary into Task, TaskDetails, TaskTime, and RepeatingTask
    classes and inputs them as new entries into the task, task_details, task_time
    and repeating_task tables respectively. 
    '''
    task = Task()
    task_details = TaskDetails()
    task_time = TaskTime()

    # Query database for class_id, task_id
    class_id = get_class_id(details['class_title'])
    task_id = get_next_task_id(class_id)
    iteration = get_next_task_iteration(class_id, task_id)

    # Insert into task table
    task.username = 'Princeton Student' # TODO UPDATE TO USE CAS AUTHENTICATION
    task.task_id = task_id
    task.class_id = class_id
    task.title = details['task_title']
    if details['repeat_freq'] != None:
        task.repeat = True
    else:
        task.repeat = False
    task.completed = False

    db.session.add(task)
    db.session.commit()

    # Insert into TaskDetails table
    task_details.username = 'Princeton Student' # TODO UPDATE TO USE CAS AUTHENTICATION
    task_details.task_id = task_id
    task_details.class_id = class_id
    task_details.iteration = iteration
    task_details.priority = details['priority']
    task_details.link = details['link']
    task_details.due_date = details['due_date']
    task_details.due_time = details['due_time']
    task.notes = details['notes']

    db.session.add(task_details)
    db.session.commit()

    # Insert into TaskTime table
    task_time.username = 'Princeton Student' # TODO UPDATE TO USE CAS AUTHENTICATION
    task_time.task_id = task_id
    task_time.class_id = class_id
    task_time.iteration = iteration
    task_time.estimated_time = details['estimated_time']
    task_time.actual_time = None
    task_time.timely_prediction = None

    db.session.add(task_time)
    db.session.commit()

    # If task is repeating, insert entry into RepeatingTasks table
    if details['repeat_freq'] != None:
        repeating_task = RepeatingTask()
        repeating_task.username = 'Princeton Student' # TODO UPDATE TO USE CAS AUTHENTICATION
        repeating_task.task_id = task_id
        repeating_task.class_id = class_id
        repeating_task.repeat_freq = details['repeat_freq']
        repeating_task.repeat_end = details['repeat_end']

        db.session.add(repeating_task)
        db.session.commit()