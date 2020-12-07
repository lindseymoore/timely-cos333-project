"""Functions to process user input and insert as new entries in the database."""

from datetime import datetime, timedelta

from timely import db
from timely.db_queries import (fetch_task_due_date, get_next_task_iteration,
                               get_task_id)
from timely.models import Class, Task, TaskIteration


# Handler function to deal with the creation of classes for input into "class" table
def class_handler(class_iteration: dict):
    """
    Takes class_iteration dictionary (user inputted fields in new Class form) with keys:
        username
        title
        dept
        num
        color
    as input.
    Configures this dictionary into Class object and inputs it as new entry in the class table.
    """

    new_class = Class(username = class_iteration["username"], title = class_iteration["title"],
                dept = class_iteration["dept"], num = class_iteration["num"],
                active_status = True, color = class_iteration["color"])

    db.session.add(new_class)
    db.session.commit()


def task_handler(details: dict):
    """
    Takes details dictionary (user inputted fields in new Task form) with keys:
        iteration_title
        class_id
        priority
        est_time
        link
        notes
        due_date
        repeat_freq
        repeat_end
        username
        group_title
    as input.
    Configures this dictionary into Task object and inputs as new entry in the task table. Calls
    _create_all_iterations to create all iterations of this task.
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

    # Create new task iteration if it is a repeating task
    due_date = datetime.strptime(details["due_date"], '%Y-%m-%d').date()
    _create_all_iterations(task, iteration, due_date, details)


def update_class_details(class_details: dict):
    """Updates a class's details based on form input dictionary class_details with keys:
        title
        class_id
        dept
        num
        color
        active_status
        username
    """
    username = class_details['username']
    class_id = class_details['class_id']
    class_info = db.session.query(Class).filter( \
                (Class.username == username) &
                (Class.class_id == class_id)).first()

    class_info.title = class_details['title']

    class_info.dept = class_details['dept']
    class_info.num = class_details['num']
    class_info.color = class_details['color']

    db.session.commit()


def update_task_details(task_details: dict):
    """Updates a task's details based on form input dictionary task_details with keys:
        task_id
        class_id
        iteration
        priority
        link
        due_date
        notes
        est_time
        repeat_freq
        repeat_end
        username
        iteration_title
    """
    username = task_details['username']
    task_id = task_details['task_id']
    iteration = task_details['iteration']

    task, task_iteration = db.session.query(Task, TaskIteration).filter( \
                (Task.username == username) &
                (Task.task_id == task_id)).join(TaskIteration, \
                (TaskIteration.username == Task.username) & \
                (TaskIteration.task_id == Task.task_id) & \
                (TaskIteration.iteration == iteration)).first()

    if task_details["repeat_freq"] != "None" and task_details["repeat_freq"] is not None:
        task.repeat = True
        print("before check for changing freq")
        if task.repeat_freq != task_details["repeat_freq"]:
            print("after changing freq check")
            task.repeat_freq = task_details["repeat_freq"]
            increment = _fetch_increment(task.repeat_freq)
            _update_repeat_freq(task, task_id, increment, int(iteration), task_details)

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
    task_iteration.notes = task_details['notes']
    task_iteration.est_time = task_details['est_time']
    if iteration == 1:
        task_iteration.timely_pred = task_details['est_time']
    task_iteration.iteration_title = task_details['iteration_title']

    db.session.commit()


def insert_canvas_tasks(task_list: list, username: str):
    """
    Takes as input task_list, a list of dictionaries with the first key being a task's status
    (new or updated), and the second key being a dictionary of informaton about the task. The
    function inserts a new task into the database, or updates the altered values of an updated task.
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

            update_task.title = task["title"]
            task_iteration.link = task["link"]
            task_iteration.due_date = datetime.strptime(task["due_date"], '%Y-%m-%d')
            task_iteration.completed = task["completed"]

            db.session.commit()


def create_new_group(task_ids: list, group_title: str, username: str):
    """
    Creates new repeating task group based on selected tasks from task grouping modal. Takes as
    input a list of task_ids, a group_title, and a username. Creates a new repeating task with title
    group_title, of which iterations will be ordered by due_date. Delete the entries in the task
    table for each of the task_ids (except for the one used for the new group), and update the
    entries in the task_iteration table for each of the new iterations of the repeating group.
    """
    is_new_group = True
    largest_group = task_ids[0]
    max_iters = 1

    # Check if we're adding to an existing group or creating a new group
    # If we're adding to an existing group, save largest_group as
    # task_id of group with most iterations
    for task_id in task_ids:
        num_iters = db.session.query(TaskIteration).filter((TaskIteration.username == username) & \
            (TaskIteration.task_id == task_id)).count()
        if num_iters > max_iters:
            max_iters = num_iters
            largest_group = task_id
            is_new_group = False

    # task_group is list of task_ids sorted by due_date
    task_group = {}
    for task_id in task_ids:
        task_group[task_id] = fetch_task_due_date(task_id, username)
    task_group = sorted(task_group, key = task_group.get)

    # if we're creating a new group, make the first iteration the one with the earliest due_date
    group_task_id = 0
    if is_new_group:
        group_task_id = task_group[0]
    else:
        # if we're adding to an existing group, make the task_id the one of the
        # largest existing group
        group_task_id = largest_group

    # Make first iteration of task repeating, change group title
    task = db.session.query(Task).filter((Task.username == username) &
        (Task.task_id == group_task_id)).first()
    task.repeat = True
    task.repeat_freq = "irregular"
    task.grouped = True
    task.title = group_title
    db.session.commit()

    # Remove first iteration from the list of task_ids sorted by due_date
    task_group.pop(task_group.index(group_task_id))

    # Update next iterations of task to be repeating tasks of first iteration. Delete their entries
    # in the Task table.
    for old_task_id in task_group:
        task_iteration = db.session.query(TaskIteration).filter((TaskIteration.username == username)
            & (TaskIteration.task_id == old_task_id)).first()

        task_iteration.iteration = get_next_task_iteration(group_task_id)
        task_iteration.task_id = group_task_id

        db.session.commit()

        db.session.query(Task).filter(Task.task_id == old_task_id).delete()
        db.session.commit()


def _fetch_increment(frequency: str):
    """Determine increment for a date object according to its repeat frequency, which can be:
        None
        daily
        weekly
        biweekly
        monthly
        irregular
    """
    if frequency == "daily":
        increment = timedelta(days=1)
    elif frequency == "weekly":
        increment = timedelta(days=7)
    elif frequency == "biweekly":
        increment = timedelta(days=14)
    elif frequency == "monthly":
        increment = timedelta(weeks=4)

    return increment


def _create_all_iterations(task, iteration: int, due_date, details: dict):
    """Creates all iterations of a given repeating task, given a task object (task), a starting
    iteration (iteration) an initial due_date (due_date), and details dict with keys:
        iteration_title
        class_id
        priority
        est_time
        link
        notes
        due_date
        repeat_freq
        repeat_end
        username
        group_title
    Creates all iterations of this given task and adds them to the task_iteration table.
    """
    print("start creating")
    # Create new task iteration if it is a repeating task
    increment = timedelta(weeks=10) # for non-repeating task
    if task.repeat:
        increment = _fetch_increment(task.repeat_freq)
        end_date = task.repeat_end
    elif task.repeat_end is None:
        increment = timedelta(days=1)
        end_date = due_date

    print("Check task repeat")

    # Creates the next iteration of a task upon completion if the repeat end is not specified
    # or next due date is before the repeat end date
    new_date = due_date

    print("new", new_date, "end", end_date)
    print("before while loop")
    while new_date <= end_date:
        print("start while")
        task_iteration = TaskIteration()
        print("iteration")
        # Insert into TaskIteration table
        task_iteration.username = details["username"]
        print("username")
        task_iteration.task_id = task.task_id
        print("task id")
        task_iteration.class_id = details["class_id"]
        print("class id")
        task_iteration.iteration_title = details["iteration_title"]
        print("assigned task title")
        task_iteration.iteration = iteration
        print("iteration")
        task_iteration.priority = details["priority"]
        print("priority")
        task_iteration.link = details["link"]
        task_iteration.due_date = new_date

        task_iteration.notes = details["notes"]
        task_iteration.completed = False

        # Insert times into TaskIteration table
        task_iteration.est_time = details["est_time"]
        task_iteration.actual_time = None
        # may need to edit display of the timely prediction to edit all subsequent iterations
        task_iteration.timely_pred = details["est_time"]

        db.session.add(task_iteration)
        db.session.commit()
        iteration += 1

        new_date += increment
        print("new date ", new_date)


def _update_repeat_freq(task, task_id, increment, iteration: int, task_details: dict):
    """
    Function to be called in update_task_details. Updates the repeat frequency of a given task by
    deleting all subsequent iterations and creating new iterations. Takes in same task_details
    dictionary as update_task_details, and takes as input a task object, task_id, iteration, and
    a time increment (as a timedelta object).
    """
    print("start of update")
    curr_iteration =  db.session.query(TaskIteration).filter((TaskIteration.task_id == task_id) & \
        (TaskIteration.iteration == int(iteration)) & \
        (TaskIteration.completed == False)).first()

    curr_due_date = curr_iteration.due_date
    curr_due_date += increment

    # Delete all subsequent tasks upon editing task repeat freq
    print("delete old iterations")
    db.session.query(TaskIteration).filter((TaskIteration.task_id == task_id) & \
        (TaskIteration.iteration > int(iteration)) & \
        (TaskIteration.completed == False)).delete()
    db.session.commit()

    iteration += 1
    print("create new")
    _create_all_iterations(task, iteration, curr_due_date, task_details)
    print("update freq")
