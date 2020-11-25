"""Functions to fetch class and task information."""

from datetime import timedelta, date, datetime
from typing import List

from sqlalchemy import desc

from timely import db
from timely.models import Class, Task, TaskIteration, User


def fetch_class_list(username: str) -> List[dict]:
    """
    Take a username.
    Return a list of dictionaries, with each dictionary representing one class with keys:
        title
        dept
        num
        color
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


def fetch_task_list(username: str, sort: str = "due_date") -> List[dict]:
    """
    Take a user with username, query the database to search for all tasks the user has inputted.
    Return a list of task dictionaries with keys:
        task_id, iteration
        title, class
        due_date, repeat, repeat_freq, repeat_end
        est_time, timely_pred, actual_time
        priority, link, notes, completed, color
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
        task_obj = {'group_title': task.title, 'class': course.title, 'task_id': task.task_id,
                    'priority': task_iteration.priority, 'repeat': task.repeat,
                    'est_time': task_iteration.est_time, 'timely_pred': task_iteration.timely_pred,
                    'link': task_iteration.link, 'notes': task_iteration.notes,
                    'due_date': task_iteration.due_date.strftime("%m/%d/%y"),
                    'repeat_freq': repeat_freq, 'repeat_end': repeat_end,
                    'completed': task_iteration.completed, 'iteration': task_iteration.iteration,
                    'color': course.color, 'actual_time': task_iteration.actual_time,
                    'iteration_title': task_iteration.iteration_title}

        if task_obj['timely_pred'] is None:
            task_obj['timely_pred'] = 0

        task_list.append(task_obj)

    if sort == "due_date":
        task_list = sorted(task_list, key = lambda task: task["due_date"], reverse=True)
    if sort == "priority":
        task_list = sorted(task_list, key = lambda task: task["priority"], reverse=True)
    if sort == "class":
        task_list = sorted(task_list, key = lambda task: task["class"], reverse=True)

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
        task_details_obj = {"group_title": task.title, "class": get_class_title(task.class_id),
                    "id": task.task_id, "repeat_freq": task.repeat_freq, "repeat_end": task.repeat_end,
                    "repeating": task.repeat, "iteration": task_iteration.iteration,
                    "priority": task_iteration.priority, "link": task_iteration.link,
                    "due_date": task_iteration.due_date.strftime("%m/%d/%y"),
                    "notes": task_iteration.notes, "est_time": task_iteration.est_time,
                    "iteration_title": task_iteration.iteration_title}
        if task_details_obj['est_time'] is None:
            task_details_obj['est_time'] = 0

    return task_details_obj

def fetch_curr_week():
    curr_date = date.today()
    offset = curr_date.weekday() #where 0 is monday

    #Determine what date corresponds to Sunday
    increment = timedelta(days=offset+1)
    day = curr_date - increment #initially sunday

    if offset == 6:  # If current date is Sunday
        day = curr_date
    
    #Create a dict of dates based on the sunday
    week = {}
    for ii in range(0, 7):
        week[ii] = day.strftime("%m/%d/%y")
        day += timedelta(days=1)

    return week

def fetch_week(week_dates: str, prev: bool):
    curr_sunday = week_dates
    sunday = datetime.strptime(curr_sunday, '%m/%d/%y')

    #Determine what date corresponds to prev or next Sunday
    if prev: 
        day = sunday - timedelta(days=7) 
    else:
        day = sunday + timedelta(days=7)

    #Create a dict of dates based on the sunday
    week = {}
    for ii in range(0, 7):
        week[ii] = day.strftime("%m/%d/%y")
        day += timedelta(days=1)

    return week


def mark_task_complete(task_id: int, username: str):
    """Update the task given by task_id as complete in the db."""
    # pylint: disable=singleton-comparison
    task, task_iteration = db.session.query(Task, TaskIteration).filter( \
                (Task.username == username) &
                (Task.task_id == task_id)).join(TaskIteration, \
                (TaskIteration.username == Task.username) & \
                (TaskIteration.task_id == Task.task_id) & \
                (TaskIteration.completed == False)).first()
    # pylint: enable=singleton-comparison

    task_iteration.completed = True
    db.session.commit()

    # Create new task iteration if it is a repeating task (and is not from Canvas)
    if task.repeat and task_iteration.canvas_id is None:
        old_date = task_iteration.due_date
        freq = task.repeat_freq

        # Increment date object according to the repeat frequency
        increment = timedelta(days=0)
        if freq == "daily":
            increment = timedelta(days=1)
        elif freq == "weekly":
            increment = timedelta(days=7)
        elif freq == "biweekly":
            increment = timedelta(days=14)
        elif freq == "monthly":
            increment = timedelta(weeks=4)

        new_date = old_date + increment

        # Creates the next iteration of a task upon completion if the repeat end is not specified
        # or next due date is before the repeat end date
        if task.repeat_end is None or new_date <= task.repeat_end:
            new_task_iteration = TaskIteration()

            # Insert into TaskIteration table
            new_task_iteration.username = task_iteration.username
            new_task_iteration.iteration_title = task.title
            new_task_iteration.task_id  = task_iteration.task_id
            new_task_iteration.class_id = task_iteration.class_id
            new_task_iteration.iteration  = task_iteration.iteration + 1
            new_task_iteration.priority = task_iteration.priority
            new_task_iteration.link = task_iteration.link
            new_task_iteration.due_date = new_date
            new_task_iteration.due_time = task_iteration.due_time

            new_task_iteration.notes = task_iteration.notes
            new_task_iteration.completed = False

            # Insert times into TaskIteration table
            new_task_iteration.est_time = task_iteration.est_time
            new_task_iteration.actual_time = None
            new_task_iteration.timely_pred = None

            db.session.add(new_task_iteration)
            db.session.commit()


def get_class_id(class_title: str) -> int:
    """Return class_id for a given class_title, where class_id is autoincrementing."""
    class_info = db.session.query(Class).filter(Class.title == class_title).first()
    return class_info.class_id


def get_class_title(class_id: int) -> str:
    """Return class_title for a given class_id."""
    class_info = db.session.query(Class).filter(Class.class_id == class_id).first()
    return class_info.title


def get_task_id(task_title: str, class_id: int) -> int:
    """Return task_id for a given task_title and class_id, where task_id is autoincrementing."""
    task_info = db.session.query(Task).filter((Task.class_id == class_id) &
                (Task.title == task_title)).first()
    return task_info.task_id


def get_next_task_iteration(task_id: int) -> int:
    """
    Return the next sequential iteration for a given task if it is repeating.
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


def get_api_key(username: str):
    """Fetch a user's Canvas API Key given their username."""
    user = db.session.query(User).filter(User.username == username).first()
    return user.api_key


def fetch_user(username: str):
    """Returns True if a user is in the User table and False otherwise."""
    user = db.session.query(User).filter(User.username == username).first()
    if user is None:
        return False
    return True
    

def get_class_id_canvas(canvas_id: int, username: str):
    """Returns the class_id of a class with a given canvas_id set by Canvas."""
    class_id = db.session.query(Class).filter((Class.canvas_id == canvas_id) & 
        (Class.username == username)).first()
    return class_id.class_id


def canvas_task_in_db(canvas_id: int, username: str):
    """Returns a tuple (True, task_info) if a task with canvas_id is already in the database, and 
       False otherwise. When working with this function, if it returns False call db.add to add a 
       new entry. Otherwise just call db.commit to update the current database entry."""
    details = db.session.query(Task, TaskIteration).filter(TaskIteration.username == username
    ).filter(TaskIteration.canvas_id == canvas_id).filter(TaskIteration.task_id == Task.task_id
    ).first()
    if details is None:
        #print("No details")
        return (False, None)
    
    task_info = {"due_date": None, "link": None, "title": None}
    task, task_iteration = details
    task_info["due_date"] = task_iteration.due_date
    task_info["link"] = task_iteration.link
    task_info["title"] = task.title
    
    return (True, task_info)


def get_class_color(class_id: int):
    """Returns the color of a class with a given class_id"""
    color = db.session.query(Class).filter(Class.class_id == class_id).first()
    return color.color


def get_task_groups(username: str, class_id: int):
    """Returns the task groups (repeating tasks) for a user within a class with a given class_id."""
    task_group = db.session.query(Task).filter((Task.username == username) & (
        Task.class_id == class_id) & (Task.repeat)).all()

    groups = []
    for task in task_group:
        task_info = {"task_id": task.task_id, "title": task.title}
        groups.append(task_info)

    return groups


def fetch_tasks_from_class(class_id: int, username: str):
    """Returns all tasks for a given user in a given class with class_id."""
    # task_id, task_title, repeating
    # If only one iteration, show due date
    task_groups = []
    task_ids = []

    tasks = db.session.query(Task).filter((Task.username == username) &
        (Task.class_id == class_id)).all()

    for task in tasks:
        info = {"task_id": task.task_id, "title": task.title, "repeat": task.repeat, 
            "due_date": None, "color": get_class_color(class_id),
             "class_title": get_class_title(class_id)}
        task_ids.append(task.task_id)
        task_groups.append(info)

    for task_id in task_ids:
        num_iterations = db.session.query(TaskIteration).filter(
            (TaskIteration.username == username) & (TaskIteration.task_id == task_id)).count()

        if num_iterations == 1:
            iteration = db.session.query(TaskIteration).filter(
                (TaskIteration.username == username) & (TaskIteration.class_id == class_id) &
                (TaskIteration.task_id == task_id)).first()
            due_date = iteration.due_date
            iteration_title = iteration.iteration_title

            # Find dict where task_id is correct, set due_date
            list(filter(lambda task: task["task_id"] == task_id, task_groups))[0]["due_date"] = due_date
            list(filter(lambda task: task["task_id"] == task_id, task_groups))[0]["iteration_title"] = iteration_title

    return task_groups


def fetch_task_due_date(task_id: int, username: str):
    """Fetches due date for task with given task_id."""
    task_iteration = db.session.query(TaskIteration).filter((TaskIteration.username == username)
        & (TaskIteration.task_id == task_id)).first()

    return task_iteration.due_date
