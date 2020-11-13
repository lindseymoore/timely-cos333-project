"""Declare application views."""

from flask import redirect, render_template, request

from timely import app
from timely.canvas_handler import fetch_canvas_courses, fetch_canvas_tasks
from timely.cas_client import CASClient
from timely.db_queries import (delete_class, delete_task, fetch_class_list,
                               fetch_task_details, fetch_task_list,
                               mark_task_complete)
from timely.form_handler import class_handler, task_handler, update_task_details
from timely.time_predict import update_completion_time, update_timely_pred

# To run the application locally with CAS authentication, check out:
# "https://stackoverflow.com/questions/50236117/"
# It may be necessary to install certificates


@app.route("/")
@app.route("/index")
def index():
    """Return the index page."""
    username = CASClient().authenticate()

    classes = fetch_class_list(username)
    tasks = fetch_task_list(username)
    return render_template("index.html",
                class_list=classes,
                task_list=tasks)


@app.route("/task_form")
def task_form():
    """
    Retrieve information from the task form and insert new table entries into the database.
    Entries being inserted into tables: task, task_details, task_time, repeating_task.
    """
    username = CASClient().authenticate()
    details = {'task_title': None, 'class_id': None, 'dept' : None, 'num': None,
    'priority': None, 'est_time': None, 'link': None, 'notes': None, 'due_date': None,
    'due_time': None, 'repeat_freq': None, 'repeat_end': None, 'username': username}

    for key, item in request.args.items():
        details[key] = item

    task_handler(details)

    return redirect("/")


@app.route("/class_form")
def class_form():
    """
    Retrieve information from the class form and insert new table entries into the database.
    Entries being inserted into tables: class.
    """
    username = CASClient().authenticate()

    class_details = {'title': None, 'dept': None, 'num': None, 'color': None, 'username': username}

    for key, item in request.args.items():
        class_details[key] = item

    class_handler(class_details)

    return redirect("/")


@app.route("/completion_form")
def completion_form():
    """
    Retrieve the status of tasks that are marked complete
    and update the database completed column.
    """
    username = CASClient().authenticate()
    task_id = request.args["task_id"]
    iteration = request.args["iteration"]
    time = request.args["time"]

    mark_task_complete(int(task_id), username)

    update_completion_time(task_id, iteration, username, time)
    update_timely_pred(task_id, iteration, username)

    return redirect("/")


@app.route("/delete_class")
def delete_class_endpoint():
    """
    Delete the class given by the request argument class_id and all of the tasks related to it."""
    delete_class(request.args["class_id"])
    return redirect("/")


@app.route("/delete_task")
def delete_task_endpoint():
    """Delete the task given by the request argument task_id."""
    delete_task(request.args["task_id"])
    return redirect("/")


@app.route('/logout', methods=['GET'])
def logout():
    """Log the user out of the application."""
    cas_client = CASClient()
    cas_client.authenticate()
    cas_client.logout()


@app.route("/canvas_class")
def canvas_class():
    """
    Fetches the classes from canvas for a particular user
    """
    username = CASClient().authenticate()
    fetch_canvas_courses("F2020", username)
    return redirect("/")


@app.route("/canvas_task")
def canvas_task():
    """
    Fetches the tasks from canvas for a particular user
    """
    username = CASClient().authenticate()
    fetch_canvas_tasks("F2020", username)
    return redirect("/")


@app.route("/task_details")
def task_details_modal():
    """Show the task details modal."""
    username = CASClient().authenticate()
    task_details = fetch_task_details(request.args["task_id"], username)
    print(task_details)
    classes = fetch_class_list(username)
    tasks = fetch_task_list(username)
    return render_template("index.html",
                class_list=classes,
                task_list=tasks,
                task_details=task_details)


@app.route("/edit_task_details")
def edit_task_details():
    username = CASClient().authenticate()
    task_details = {"title": None, "task_id": None, "class": None, "repeat": None,
                "priority": None, "link": None, "due_date": None, "notes": None, 
                "est_time": None, "repeat_freq": None, "repeat_end": None, "due_time": None, 
                "username": username}

    for key, item in request.args.items():
        task_details[key] = item

    update_task_details(task_details)
   
    return redirect("/")
