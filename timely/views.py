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
# , update_class_details
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

    details['group_title'] = details['task_title']

    task_handler(details)

    return redirect("/list")


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

    return redirect("/list")

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
        return redirect("/list")

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
    return redirect("/list")

@app.route("/calendar/delete_task")
@app.route("/delete_task")
def delete_task_endpoint():
    """Delete the task given by the request argument task_id."""
    delete_task(request.args["task_id"])
    if request.path == "/calendar/delete_task":
        return redirect("/calendar")
    else:
        return redirect("/list")


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

    user = db.session.query(User).filter(User.username == username).first()
    if user is None:
        new_user = User(username = username, api_key = api_key)
        db.session.add(new_user)
        db.session.commit()
    else:
        user.api_key = api_key
        db.session.commit()
        
    return redirect("/list")


@app.route("/canvas_class")
def canvas_class():
    """
    Fetches the classes from canvas for a particular user
    """
    username = CASClient().authenticate()
    fetch_canvas_courses("F2020", username)
    return redirect("/list")


@app.route("/canvas_task")
def canvas_task():
    """
    Fetches the tasks from canvas for a particular user
    """
    username = CASClient().authenticate()
    fetch_canvas_tasks("F2020", username)
    return redirect("/list")


@app.route("/task_details_calendar_view")
@app.route("/task_details_list_view")
def task_details_modal():
    """Show the task details modal."""    
    username = CASClient().authenticate()
    task_id = request.args["task_id"]
    iteration = request.args["iteration"]
    task_details = fetch_task_details(task_id, iteration, username)
    #print(task_details)
    classes = fetch_class_list(username)
    week_dates = fetch_curr_week()

    if request.path == "/task_details_calendar_view":
        template = "calendar.html"
        tasks = fetch_task_calendar_view(username)
    else:
        template = "index.html"
        tasks = fetch_task_list_view(username)

    # For tasks that have iteration time data
    if task_details["repeating"] is True:
        curr_iteration = task_details["iteration"]
        #print(curr_iteration)
        times = fetch_graph_times(task_id, curr_iteration, username)
        labels = list(range(1, curr_iteration))
        actual_values = times["actual_times"]
        predicted_values = times["predicted_times"]
        print(labels)
        print(times)
        
        return render_template(template,
                class_list=classes,
                task_list=tasks,
                task_details=task_details,
                week_dates=week_dates,
                actual_values=actual_values,
                predicted_values=predicted_values, 
                labels=labels)

    return render_template(template,
                class_list=classes,
                task_list=tasks,
                task_details=task_details,
                week_dates=week_dates)

                           
@app.route("/edit_task_details")
def edit_task_details():
    """Edit task details modal endpoint."""
    username = CASClient().authenticate()
    # Potentially change class_id to class
    task_details = {"group_title": None, "task_id": None,"class_id": None, "repeat": None, "iteration": None,
                "priority": None, "link": None, "due_date": None, "notes": None, 
                "est_time": None, "repeat_freq": None, "repeat_end": None, "due_time": None, 
                "username": username, "iteration_title": None, "iteration": None}

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

    return redirect("/list")


@app.route("/canvas_import", methods=["POST"])
def canvas_import():
    """Handle the canvas import modal."""
    username = CASClient().authenticate()
    task_list = []
    for value in request.form.values():
        # json.loads returns dictionary, first key is status (new or updated), second is task itself
        task_list.append(json.loads(value))
    
    insert_canvas_tasks(task_list, username)
    return redirect("/list")


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
    group_title = ""

    for value in request.form.values():
        try:
            task_id = int(value)
            task_ids.append(task_id)
        except ValueError:
            group_title = value

    #print("TASK_IDS", task_ids)
    create_new_group(task_ids, group_title, username)
    return redirect("/list")
   

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


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 404
