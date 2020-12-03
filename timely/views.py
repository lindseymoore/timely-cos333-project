"""Declare application views."""

import json

from flask import redirect, render_template, request

from timely import app, db
from timely.canvas_handler import fetch_canvas_courses, fetch_canvas_tasks
from timely.cas_client import CASClient
from timely.db_queries import (delete_class, delete_task,
                               fetch_available_colors, fetch_class_details,
                               fetch_class_list, fetch_curr_week,
                               fetch_task_calendar_view, fetch_task_details,
                               fetch_task_list_view, fetch_tasks_from_class,
                               fetch_user, fetch_week, mark_task_complete,
                               uncomplete_task)

from timely.form_handler import (class_handler, create_new_group,
                                 insert_canvas_tasks, task_handler,
                                 update_class_details, update_task_details)
from timely.models import User
from timely.time_predict import (fetch_graph_times, update_completion_time,
                                 update_timely_pred)

# To run the application locally with CAS authentication, check out:
# "https://stackoverflow.com/questions/50236117/"
# It may be necessary to install certificates


@app.route("/list")
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
    colors = fetch_available_colors(username)
    return render_template("index.html",
                class_list=classes,
                task_list=tasks,
                user_info = user,
                colors = colors)

@app.route("/")
def landing():
    """Return the landing page."""
    # Redirects to list if user is logged in
    try:
        CASClient().authenticate()
    except:
        return render_template("landing.html")
    else:
        return redirect("/list")


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
    if "public" in request.args.keys():
        public = True
    else:
        public = False
    return render_template("about.html", public=public)


@app.route("/feedback")
def feedback():
    """Display the feedback page."""
    return render_template("feedback.html", public=True)


@app.route("/task_form", methods=["POST"])
def task_form():
    """
    Retrieve information from the task form and insert new table entries into the database.
    Entries being inserted into tables: task, task_details, task_time, repeating_task.
    """
    username = CASClient().authenticate()
    details = {'task_title': None, 'class_id': None, 'dept' : None, 'num': None,
    'priority': None, 'est_time': None, 'link': None, 'notes': None, 'due_date': None,
    'due_time': None, 'repeat_freq': None, 'repeat_end': None, 'username': username}

    for key, item in request.form.items():
        details[key] = item

    details['group_title'] = details['task_title']

    task_handler(details)
    return json.dumps({"success":True})


@app.route("/class_form", methods=["POST"])
def class_form():
    """
    Retrieve information from the class form and insert new table entries into the database.
    Entries being inserted into tables: class.
    """
    username = CASClient().authenticate()

    class_details = {'title': None, 'dept': None, 'num': None, 'color': None, 'username': username}

    for key, item in request.form.items():
        class_details[key] = item

    class_handler(class_details)

    return json.dumps({"success":True})


@app.route("/completion_form", methods=["POST"])
def completion_form():
    """
    Retrieve the status of tasks that are marked complete
    and update the database completed column.
    """
    username = CASClient().authenticate()
    task_id = request.args["task_id"]
    iteration = request.args["iteration"]
    time = request.form["time"]

    mark_task_complete(int(task_id), int(iteration), username)

    update_completion_time(task_id, iteration, username, time)
    update_timely_pred(task_id, iteration, username)
    
    return json.dumps({"success":True})


@app.route("/uncomplete", methods=["POST"])
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

    return json.dumps({"success":True})


@app.route("/delete_class", methods=["POST"])
def delete_class_endpoint():
    """
    Delete the class given by the request argument class_id and all of the tasks related to it."""
    delete_class(request.args["class_id"])
    return json.dumps({"success":True})


@app.route("/delete_task", methods=["POST"])
def delete_task_endpoint():
    """Delete the task given by the request argument task_id."""
    delete_task(request.args["task_id"])
    return json.dumps({"success":True})


@app.route('/logout', methods=['GET'])
def logout():
    """Log the user out of the application."""
    cas_client = CASClient()
    cas_client.authenticate()
    cas_client.logout()


@app.route("/canvas_key", methods=["POST"])
def canvas_key():
    """
    Inserts the Canvas API Key for a particular user
    """
    username = CASClient().authenticate()
    api_key = request.form["api_key"]

    user = db.session.query(User).filter(User.username == username).first()
    if user is None:
        new_user = User(username = username, api_key = api_key)
        db.session.add(new_user)
        db.session.commit()
    else:
        user.api_key = api_key
        db.session.commit()

    return json.dumps({"success":True})


@app.route("/canvas_class", methods=["POST"])
def canvas_class():
    """
    Fetches the classes from canvas for a particular user
    """
    username = CASClient().authenticate()
    fetch_canvas_courses("F2020", username)
    return json.dumps({"success":True})


@app.route("/task_details")
def task_details_modal():
    """Show the task details modal."""
    username = CASClient().authenticate()
    task_id = request.args["task_id"]
    iteration = request.args["iteration"]
    task_details = fetch_task_details(task_id, iteration, username)

    # If task_details is None (which will occur if user manually inputs task_id they do not have 
    # access to) then raise a 403 error
    if task_details is None:
        return json.dumps({"success": False}), 403

    return json.dumps(task_details, default=str)


@app.route("/edit_task_details", methods=["POST"])
def edit_task_details():
    """Edit task details modal."""
    username = CASClient().authenticate()
    # Potentially change class_id to class
    task_details = {"task_id": None, "class_id": None, "iteration": None,
                "priority": None, "link": None, "due_date": None, "notes": None,
                "est_time": None, "repeat_freq": None, "repeat_end": None,
                "username": username, "iteration_title": None}

    for key, item in request.form.items():
        task_details[key] = item

    if task_details["repeat_end"] == "":
        task_details["repeat_end"] = None

    task_details["task_id"] = int(request.args["task_id"])
    task_details["iteration"] = int(request.args["iteration"])

    update_task_details(task_details)

    return json.dumps({"success":True})


@app.route("/get_graph_data", methods=["GET"])
def get_graph_data():
    username = CASClient().authenticate()
    task_id = request.args["task_id"]
    iteration = request.args["iteration"]
    # Contains labels, actual_times, and predicted_times
    times = fetch_graph_times(task_id, iteration, username)

    return json.dumps(times, default=dict)# dumps is for str formatting dict


@app.route("/edit_class_details", methods=["POST"])
def edit_class_details():
    """Edit class details modal."""
    username = CASClient().authenticate()
    class_details = {"title": None, "class_id": None, "dept": None, "num": None,
                "color": None, "active_status": None, "username": username}

    class_details["class_id"] = request.args["class_id"]
    for key, item in request.form.items():
        class_details[key] = item

    update_class_details(class_details)

    return json.dumps({"success":True})


@app.route("/canvas_import", methods=["POST"])
def canvas_import():
    """Handle the canvas import modal."""
    username = CASClient().authenticate()
    task_list = []
    for value in request.form.values():
        # json.loads returns dictionary, first key is status (new or updated), second is task itself
        task_list.append(json.loads(value))

    insert_canvas_tasks(task_list, username)
    return json.dumps({"success":True})


@app.route("/class_details")
def class_details_json():
    """Return class details as JSON for the class details modal."""
    username = CASClient().authenticate()
    class_details = fetch_class_details(request.args["class_id"], username)

    # If task_details is None (which will occur if user manually inputs task_id they do not have 
    # access to) then raise a 403 error
    if class_details is None:
        return json.dumps({"success": False}), 403

    return json.dumps(class_details, default=str)


@app.route("/get_canvas_tasks")
def get_canvas_tasks():
    """Fetches new and updated tasks from Canvas to be displayed in Canvas import modal."""
    tasks = fetch_canvas_tasks("F2020", CASClient().authenticate())
    return json.dumps(tasks, default=str)


@app.route("/get_classes")
def get_classes():
    """Return all classes."""
    classes = fetch_class_list(CASClient().authenticate())
    return json.dumps(classes, default=str)


@app.route("/group_task", methods=["POST"])
def group_tasks():
    """Groups tasks into repeating tasks based on users selection in task grouping modal."""
    username = CASClient().authenticate()
    task_ids = []
    group_title = ""

    for value in request.form.values():
        try:
            task_id = int(value)
            task_ids.append(task_id)
        except ValueError:
            group_title = value

    #print("TASK_IDS", task_ids)
    create_new_group(task_ids, group_title, username)
    return json.dumps({"success":True})


@app.route("/get_tasks")
def get_tasks():
    """
    Fetches all tasks associated with a given class and returns information in JSON format.
    If class is left as none, return all tasks for all classes.
    """
    username = CASClient().authenticate()
    class_id = request.args["class_id"]
    tasks = fetch_tasks_from_class(class_id, username)
    
    # Set null due_dates to 'Group' to avoid showing null due dates on modal
    for task in tasks:
        if task["due_date"] is None:
            task["due_date"] = "Group"
        if task["title"] is None or task["title"] == "":
            task["title"] = task["iteration_title"]

    return json.dumps(tasks, default=str)


@app.errorhandler(403)
@app.route("/403")
def forbidden():
    """Render the 403 page."""
    return render_template("403.html"), 403


@app.errorhandler(404)
def page_not_found(e):
    """Render the 404 page."""
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    """Render the 500 page."""
    return render_template("500.html"), 404
