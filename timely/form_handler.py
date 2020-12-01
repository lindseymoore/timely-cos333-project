"""Functions to process user input and insert as new entries in the database."""

from datetime import timedelta, date, datetime

from sqlalchemy import desc

from timely import db
from timely.db_queries import (fetch_task_due_date, get_next_task_iteration,
                               get_task_id)
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

    # Insert into task table
    task.username = details["username"]
    task.class_id = details["class_id"]
    task.title = details["group_title"]
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
    task_id = get_task_id(details['group_title'], details['class_id'])
    iteration = get_next_task_iteration(task_id)


    # Insert into TaskIteration table
    task_iteration.username = details["username"]
    task_iteration.iteration_title = details["task_title"]
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

    # Create new task iteration if it is a repeating task
    due_date = datetime.strptime(details["due_date"], '%Y-%m-%d').date()
    create_all_iterations(task, iteration, due_date, details)

    
def fetch_increment(frequency: str):
    """Determine increment for a date object according to the repeat frequency"""
    if frequency == "daily":
        increment = timedelta(days=1)
    elif frequency == "weekly":
        increment = timedelta(days=7)
    elif frequency == "biweekly":
        increment = timedelta(days=14)
    elif frequency == "monthly":
        increment = timedelta(weeks=4)
    
    return increment

  
def create_all_iterations(task, iteration: int, due_date, details: dict):
    """Creates all iterations of a given repeating task."""
    # Create new task iteration if it is a repeating task
    if task.repeat:
        increment = fetch_increment(task.repeat_freq)
        end_date = task.repeat_end
    elif task.repeat_end is None:
        increment = timedelta(days=1)
        end_date = due_date

    # Creates the next iteration of a task upon completion if the repeat end is not specified
    # or next due date is before the repeat end date
    new_date = due_date

    print(new_date, end_date)
    while (new_date <= end_date):
        task_iteration = TaskIteration()
        # Insert into TaskIteration table
        task_iteration.username = details["username"]
        task_iteration.task_id = task.task_id
        task_iteration.class_id = details['class_id']
        task_iteration.iteration = iteration
        #task_iteration.iteration_title = details["task_title"] -> add this line in
        task_iteration.priority = details["priority"]
        task_iteration.link = details["link"]
        task_iteration.due_date = new_date
        task_iteration.due_time = details["due_time"]

        task_iteration.notes = details["notes"]
        task_iteration.completed = False

        # Insert times into TaskIteration table
        task_iteration.est_time = details["est_time"]
        task_iteration.actual_time = None
        task_iteration.timely_pred = details["est_time"] # may need to edit display of the timely prediction to edit all subsequent iterations

        db.session.add(task_iteration)
        db.session.commit()
        iteration += 1
        new_date += increment


def update_task_details(task_details: dict):
    """Updates a task's details based on form input."""
    username = task_details['username']
    task_id = task_details['task_id']
    iteration = task_details['iteration']
    #print("task_id", task_id)

    task, task_iteration = db.session.query(Task, TaskIteration).filter( \
                (Task.username == username) &
                (Task.task_id == task_id)).join(TaskIteration, \
                (TaskIteration.username == Task.username) & \
                (TaskIteration.task_id == Task.task_id) & \
                (TaskIteration.iteration == iteration)).first()

    # print(task)
    # print(task_iteration)
    task.title = task_details['group_title']

    if task_details["repeat_freq"] != "None" and task_details["repeat_freq"] is not None:
        task.repeat = True
        if task.repeat_freq != task_details["repeat_freq"]:
            task.repeat_freq = task_details["repeat_freq"]
            increment = fetch_increment(task.repeat_freq)
            update_repeat_freq(task, task_id, increment, int(iteration), task_details)
        
        if task_details["repeat_end"] != "None":
            task.repeat_end = task_details["repeat_end"]
        else:
            task.repeat_end = None
    else:
        task.repeat = False
  
    if task.repeat:
        task.repeat_freq = task_details['repeat_freq']
        task.repeat_end = task_details['repeat_end']

    if task_details['priority'] == 'None' or task_details['priority'] is None:
        task_iteration.priority = None
    else:
        task_iteration.priority = task_details['priority']
    task_iteration.link = task_details['link']
    task_iteration.due_date = task_details['due_date']
    task_iteration.due_time = task_details['due_time']
    task_iteration.notes = task_details['notes']
    task_iteration.est_time = task_details['est_time']
    task_iteration.iteration_title = task_details['iteration_title']

    db.session.commit()


def update_repeat_freq(task, task_id, increment, iteration: int, task_details: dict):
    """Updates the repeat frequency of a given task by deleting all subsequent iterations 
    and creating new iterations."""
    curr_iteration =  db.session.query(TaskIteration).filter((TaskIteration.task_id == task_id) & \
        (TaskIteration.iteration == int(iteration)) & \
        (TaskIteration.completed == False)).first()

    curr_due_date = curr_iteration.due_date
    curr_due_date += increment

    # Delete all subseqeunt tasks upon editing task repeat freq
    db.session.query(TaskIteration).filter((TaskIteration.task_id == task_id) & \
        (TaskIteration.iteration > int(iteration)) & \
        (TaskIteration.completed == False)).delete()
    db.session.commit()

    iteration += 1
    create_all_iterations(task, iteration, curr_due_date, task_details)


def update_class_details(class_details: dict):
    """Updates a class's details based on form input."""
    username = class_details['username']
    class_id = class_details['class_id']
    print("class_id", class_id)
    class_info = db.session.query(Class).filter( \
                (Class.username == username) &
                (Class.class_id == class_id)).first()

    class_info.title = class_details['title']

    class_info.dept = class_details['dept']
    class_info.num = class_details['num']
    class_info.color = class_details['color']

    db.session.commit()


def insert_canvas_tasks(task_list: list, username: str):
    """
    Takes as input task_list, a list of dictionaries with the first key being a task's status
    (new or updated), and the second key beind a dictionary of informaton about the task. The
    function inserts a new task into the database, or udpates the altered values of an updated task.
    """
    for task_info in task_list:
        new_status = task_info["status"]
        task = task_info["task"]

        if new_status == "new":
            new_task = Task()
            task_iteration = TaskIteration()

            new_task.username = username
            new_task.class_id = task["class_id"]
            new_task.title = task["title"]

            db.session.add(new_task)
            db.session.commit()

            task_id = get_task_id(task["title"], task["class_id"])
            iteration = get_next_task_iteration(task_id)
            task_iteration.iteration_title = task["title"]
            task_iteration.username = username
            task_iteration.task_id = task_id
            task_iteration.class_id = task["class_id"]
            task_iteration.iteration = iteration
            task_iteration.link = task["link"]
            task_iteration.due_date = datetime.strptime(task["due_date"], '%Y-%m-%d')
            task_iteration.canvas_id = task["canvas_task_id"]
            task_iteration.completed = task["completed"]
            task_iteration.priority = task["priority"]

            db.session.add(task_iteration)
            db.session.commit()

        else:
            update_task, task_iteration = db.session.query(Task, TaskIteration).filter(
                TaskIteration.username == username).filter(
                TaskIteration.canvas_id == task["canvas_task_id"]).filter(
                    TaskIteration.task_id == Task.task_id).first()

            # print(update_task.title)
            # print(task_iteration.link, task_iteration.due_date)

            update_task.title = task["title"]
            #print(task["title"])
            task_iteration.link = task["link"]
            #print(task["link"])
            task_iteration.due_date = datetime.strptime(task["due_date"], '%Y-%m-%d')
            #print(datetime.strptime(task["due_date"], '%Y-%m-%d'))
            task_iteration.completed = task["completed"]
            #print(task["completed"])

            db.session.commit()


def create_new_group(task_ids: list, group_title: str, username: str):
    """Function to create new repeating task group based on task grouping modal."""
    group_task_id = task_ids[0]
    for task_id in task_ids:
        try:
            group_task_id = get_task_id(group_title, task_id)
        except Exception:
            continue

    # task_group = {}
    # for task_id in task_ids:
    #     task_group[task_id] = fetch_task_due_date(task_id, username)
    # task_group = sorted(task_group, key = task_group.get)
    # group_task_id = task_group[0]
    task = db.session.query(Task).filter((Task.username == username) &
        (Task.task_id == group_task_id)).first()

    # Make first iteration of task repeating
    task.repeat = True
    task.title = group_title

    #print(task.repeating)
    #print(task.title)
    db.session.commit()

    # Update next iterations of task to be repeating tasks of first iteration. Delete their entries
    # in the Task table.

    task_ids.pop(task_ids.index(group_task_id))
    for old_task_id in task_ids:
        task_iteration = db.session.query(TaskIteration).filter((TaskIteration.username == username)
            & (TaskIteration.task_id == old_task_id)).first()
        
        task_iteration.iteration = get_next_task_iteration(group_task_id)
        task_iteration.task_id = group_task_id
        #print(task_iteration)

        db.session.commit()

        db.session.query(Task).filter(Task.task_id == old_task_id).delete()
        db.session.commit()

    # for iteration, old_task_id in enumerate(task_group[1:]):
    #     # Update task_id and iteration of next task_iteration in the group
    #     task_iteration = db.session.query(TaskIteration).filter((TaskIteration.username == username)
    #         & (TaskIteration.task_id == old_task_id)).first()
     
    #     task_iteration.task_id = group_task_id
    #     task_iteration.iteration = iteration + 2

    #     db.session.commit()

    #     # Delete entry in Task table from database - unnecessary because it's now repeating
    #     db.session.query(Task).filter(Task.task_id == old_task_id).delete()
    #     db.session.commit()
