"""Declare application views."""

from flask import redirect, render_template, request

from timely import app
from timely.db_queries import fetch_class_list, fetch_task_list, mark_task_complete
from timely.form_handler import class_handler, task_handler


@app.route("/")
@app.route("/index")
def index():
    """Return the index page."""
    #model = User.query.filter_by(username="dlipman").first()
    classes = fetch_class_list("dlipman")
    tasks = fetch_task_list("dlipman")
    return render_template("index.html",
                class_list=classes,
                task_list=tasks)
                #param=model.password)

@app.route("/task_form")
def task_form():
    """
    Retrieve information from the task form and insert new table entries into the database.
    Entries being inserted into tables: task, task_details, task_time, repeating_task.
    """

    details = {"task_title": None, "class_title": None, "dept" : None, "num": None,
    "priority": None, "est_time": None, "link": None, "notes": None, "due_date": None,
    "due_time": None, "repeat_freq": None, "repeat_end": None}

    for key, item in request.args.items():
        details[key] = item

    task_handler(details)

    return redirect("/")

@app.route("/class_form")
def class_form():
    """Retrieve information from the class form and insert new table entries into the database.
       Entries being inserted into tables: class."""
    class_details = {"title": None, "dept": None, "num": None, "color": None}

    for key, item in request.args.items():
        class_details[key] = item

    class_handler(class_details)

    return redirect("/")

@app.route("/completion_form")
def completion_form():
    """Retrieves the status of tasks that are marked complete and updates the database completed column."""
    form_task_ids = request.form.getlist("task_ids")
    for form_complete_id in form_task_ids:
            mark_task_complete(int(form_complete_id))
    return redirect("/")
    
