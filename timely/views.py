"""Declare application views."""

import json

from flask import redirect, render_template, request

from timely import app, db
from timely.canvas_handler import fetch_canvas_courses, fetch_canvas_tasks
from timely.cas_client import CASClient
from timely.db_queries import (delete_class, delete_task, fetch_class_details,
                                fetch_class_list, fetch_task_details,
                                fetch_task_list_view, fetch_task_calendar_view,
                                fetch_user, mark_task_complete, uncomplete_task,
                                fetch_curr_week, fetch_tasks_from_class,
                                fetch_week)

from timely.models import User
# , update_class_details
from timely.form_handler import (class_handler, create_new_group, insert_canvas_tasks, task_handler,
                                update_task_details, update_class_details)
from timely.time_predict import update_completion_time, update_timely_pred, fetch_graph_times

# To run the application locally with CAS authentication, check out:
# "https://stackoverflow.com/questions/50236117/"
# It may be necessary to install certificates


@app.route("/")
@app.route("/index")
def index():
    """Return the index page."""
    username = CASClient().authenticate()
    if "sort" in request.args:
        sort = request.args['sort']
    else:
        sort = "due_date"

    classes = fetch_class_list(username)
    tasks = fetch_task_list_view(username, sort)
    user = fetch_user(username)
    return render_template("index.html",
                class_list=classes,
                task_list=tasks,
                user_info = user)


@app.route("/calendar")
def calendar():
    """Return the calendar page."""
    username = CASClient().authenticate()
    classes = fetch_class_list(username)
    tasks = fetch_task_calendar_view(username)
    week_dates = fetch_curr_week()
    return render_template("calendar.html",
                class_list=classes,
                task_list=tasks,
                week_dates=week_dates)

@app.route("/calendar/next_week")
def next_week():
    """Return the calendar page."""
    username = CASClient().authenticate()
    classes = fetch_class_list(username)
    tasks = fetch_task_calendar_view(username)
    week_dates = request.args["week-dates"]
    next_week_dates = fetch_week(week_dates, False)
    return render_template("calendar.html",
                class_list=classes,
                task_list=tasks,
                week_dates=next_week_dates)

@app.route("/calendar/prev_week")
def prev_week():
    """Return the calendar page."""
    username = CASClient().authenticate()
    classes = fetch_class_list(username)
    tasks = fetch_task_calendar_view(username)
    week_dates = request.args["week-dates"]
    # week_dates = eval(week_dates)
    prev_week_dates = fetch_week(week_dates, True)
    return render_template("calendar.html",
                class_list=classes,
                task_list=tasks,
                week_dates=prev_week_dates)

@app.route("/about")
def about():
    """Display about page."""
    return render_template("about.html")


@app.route("/feedback")
def feedback():
    """Display the feedback page."""
    return render_template("feedback.html")


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

@app.route("/calendar/completion_form")
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

    mark_task_complete(int(task_id), int(iteration), username)

    update_completion_time(task_id, iteration, username, time)
    update_timely_pred(task_id, iteration, username)
    
    if request.path == "/calendar/completion_form":
        return redirect("/calendar")
    else:
        return redirect("/")

@app.route("/calendar/uncomplete")
@app.route("/uncomplete")
def uncomplete():
    """
    Retrieve the status of tasks that are marked complete
    and update the database completed column.
    """
    username = CASClient().authenticate()
    task_id = request.args["task_id"]
    iteration = request.args["iteration"]
    time = None

    uncomplete_task(int(task_id), int(iteration), username)

    update_completion_time(task_id, iteration, username, time)
    if int(iteration) > 1:
        update_timely_pred(task_id, iteration, username)
    
    if request.path == "/calendar/uncomplete":
        return redirect("/calendar")
    else:
        return redirect("/")

@app.route("/delete_class")
def delete_class_endpoint():
    """
    Delete the class given by the request argument class_id and all of the tasks related to it."""
    delete_class(request.args["class_id"])
    return redirect("/")

@app.route("/calendar/delete_task")
@app.route("/delete_task")
def delete_task_endpoint():
    """Delete the task given by the request argument task_id."""
    delete_task(request.args["task_id"])
    if request.path == "/calendar/delete_task":
        return redirect("/calendar")
    else:
        return redirect("/")


@app.route('/logout', methods=['GET'])
def logout():
    """Log the user out of the application."""
    cas_client = CASClient()
    cas_client.authenticate()
    cas_client.logout()


@app.route("/canvas_key")
def canvas_key():
    """
    Inserts the Canvas API Key for a particular user
    """
    username = CASClient().authenticate()
    api_key = request.args["api_key"]
    new_user = User(username = username, api_key = api_key)
    db.session.add(new_user)
    db.session.commit()
    return redirect("/")


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


@app.route("/task_details_list_view")
def task_details_modal_list():
    """Show the task details modal."""
    username = CASClient().authenticate()
    task_id = request.args["task_id"]
    iteration = request.args["iteration"]
    task_details = fetch_task_details(task_id, iteration, username)
    print(task_details)
    classes = fetch_class_list(username)
    tasks = fetch_task_list_view(username)

    # For tasks that have iteration time data
    if task_details["repeating"] is True:
        curr_iteration = task_details["iteration"]
        print(curr_iteration)
        times = fetch_graph_times(task_id, curr_iteration, username)
        labels = list(range(1, curr_iteration))
        actual_values = times["actual_times"]
        predicted_values = times["predicted_times"]
        print(labels)
        print(times)
        return render_template("index.html",
                    class_list=classes,
                    task_list=tasks,
                    task_details=task_details,
                    actual_values=actual_values,
                    predicted_values=predicted_values, 
                    labels=labels)
    print("HELLOWORLD")

    return render_template("index.html",
                    class_list=classes,
                    task_list=tasks,
                    task_details=task_details)

@app.route("/task_details_calendar_view")
def task_details_modal_calendar():
    """Show the task details modal."""
    username = CASClient().authenticate()
    iteration = request.args["iteration"]
    task_details = fetch_task_details(request.args["task_id"], iteration, username)
    classes = fetch_class_list(username)
    tasks = fetch_task_calendar_view(username)
    week_dates = fetch_curr_week()
    return render_template("calendar.html",
                class_list=classes,
                task_list=tasks,
                task_details=task_details,
                week_dates=week_dates)

@app.route("/edit_task_details")
def edit_task_details():
    username = CASClient().authenticate()
    task_details = {"title": None, "task_id": None, "class": None, "repeat": None, "iteration": None,
                "priority": None, "link": None, "due_date": None, "notes": None, 
                "est_time": None, "repeat_freq": None, "repeat_end": None, "due_time": None, 
                "username": username}

    for key, item in request.args.items():
        task_details[key] = item

    update_task_details(task_details)
   
    return redirect("/")


@app.route("/edit_class_details")
def edit_class_details():
    """Edit the class details modal."""
    username = CASClient().authenticate()
    class_details = {"title": None, "class_id": None, "dept": None, "num": None,
                "color": None, "active_status": None, "username": username}

    for key, item in request.args.items():
        class_details[key] = item

    update_class_details(class_details)

    return redirect("/")


@app.route("/canvas_import", methods=["POST"])
def canvas_import():
    """Handle the canvas import modal."""
    username = CASClient().authenticate()
    task_list = []
    for value in request.form.values():
        # json.loads returns dictionary, first key is status (new or updated), second is task itself
        task_list.append(json.loads(value))
    
    insert_canvas_tasks(task_list, username)
    return redirect("/")


@app.route("/class_details")
def class_details_modal():
    """Show the class details modal."""
    username = CASClient().authenticate()
    class_details = fetch_class_details(request.args["class_id"], username)
    print(class_details)
    classes = fetch_class_list(username)
    tasks = fetch_task_list_view(username)
    return render_template("index.html",
                class_list=classes,
                task_list=tasks,
                class_details=class_details)


@app.route("/get_canvas_tasks")
def get_canvas_tasks():
    """Fetches new and updated tasks from Canvas to be displayed in Canvas import modal."""
    tasks = fetch_canvas_tasks("F2020", CASClient().authenticate())
    return json.dumps(tasks, default=str)


@app.route("/get_classes")
def get_classes():
    """Return all classes."""
    classes = fetch_class_list(CASClient().authenticate())
    return json.dumps(classes)


@app.route("/group_task", methods=["POST"])
def group_tasks():
    """Groups tasks into repeating tasks based on users selection in task grouping modal."""
    username = CASClient().authenticate()
    task_ids = []
    for task_id in request.form.values():
        task_ids.append(task_id)

    #print("TASK_IDS", task_ids)
    create_new_group(task_ids, username)
    return redirect("/")
   

@app.route("/get_tasks")
def get_tasks():
    """
    Fetches all tasks associated with a given task and returns information in JSON format.
    If class is left as none, return all tasks for all classes.
    """
    username = CASClient().authenticate()
    class_id = request.args["class_id"]
    tasks = fetch_tasks_from_class(class_id, username)
    return json.dumps(tasks, default=str)