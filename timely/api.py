"""Declare API (endpoints that do NOT delvier HTML)."""

import json

from flask import request

from timely import app, db
from timely.canvas_handler import (fetch_canvas_courses, fetch_canvas_tasks,
                                   fetch_current_semester, validate_api_key)
from timely.cas_client import CASClient
from timely.db_queries import (fetch_class_details, fetch_class_list,
                               fetch_task_details, fetch_tasks_from_class)
from timely.db_updates import (delete_all_iterations, delete_class,
                               delete_iteration, insert_canvas_key,
                               mark_task_complete, uncomplete_task)
from timely.form_handler import (class_handler, create_new_group,
                                 insert_canvas_tasks, task_handler,
                                 update_class_details, update_task_details)
from timely.models import User
from timely.time_predict import (fetch_graph_times, update_completion_time,
                                 update_timely_pred)

# NOTE: To run the application locally with CAS authentication, check out:
# "https://stackoverflow.com/questions/50236117/"
# It may be necessary to install certificates


@app.route("/create-task-form", methods=["POST"])
def create_task_form():
    """
    Method(s): POST

    Take a form of the following fields:
        task_title: str
        class_id: int
        priority: int
        est_time: float
        link: str
        notes: str
        due_date: Date
        repeat_freq: str
        repeat_end: Date

    Create a new task.
    """
    username = CASClient().authenticate()
    details = {'task_title': None, 'class_id': None,
    'priority': None, 'est_time': None, 'link': None, 'notes': None, 'due_date': None,
    'repeat_freq': None, 'repeat_end': None, 'username': username}

    for key, item in request.form.items():
        details[key] = item

    details['group_title'] = details['task_title']

    try:
        task_handler(details)
    except:
        return json.dumps({"success": False}), 500
    else:
        return json.dumps({"success": True}), 200


@app.route("/create-class-form", methods=["POST"])
def create_class_form():
    """
    Method(s): POST

    Take a form of the following fields:
        title: str
        dept: str
        num: int
        color: str

    Create a new class.
    """
    username = CASClient().authenticate()

    class_details = {'title': None, 'dept': None, 'num': None, 'color': None, 'username': username}

    for key, item in request.form.items():
        class_details[key] = item

    try:
        class_handler(class_details)
    except:
        return json.dumps({"success": False}), 500
    else:
        return json.dumps({"success": True}), 200


@app.route("/completion-form", methods=["POST"])
def completion_form():
    """
    Method(s): POST

    Take request args of the following fields:
        task_id: int
        iteration: int

    Take a form of the following fields:
        time: float

    Complete a task iteration.
    """
    username = CASClient().authenticate()
    task_id = request.args["task_id"]
    iteration = request.args["iteration"]
    time = request.form["time"]

    try:
        mark_task_complete(int(task_id), int(iteration), username)
        update_completion_time(task_id, iteration, username, time)
        update_timely_pred(task_id, iteration, username)
    except:
        return json.dumps({"success": False}), 500
    else:
        return json.dumps({"success": True}), 200


@app.route("/uncomplete", methods=["POST"])
def uncomplete():
    """
    Method(s): POST

    Take request args of the following fields:
        task_id: int
        iteration: int

    Uncomplete a task iteration.
    """
    username = CASClient().authenticate()
    task_id = request.args["task_id"]
    iteration = request.args["iteration"]
    time = None

    try:
        uncomplete_task(int(task_id), int(iteration), username)

        update_completion_time(task_id, iteration, username, time)
        if int(iteration) > 1:
            update_timely_pred(task_id, iteration, username)
    except:
        return json.dumps({"success": False}), 500
    else:
        return json.dumps({"success": True}), 200


@app.route("/delete-class", methods=["POST"])
def delete_class_endpoint():
    """
    Method(s): POST

    Take request args of the following fields:
        class_id: int

    Delete a class and all its associated tasks.
    """
    try:
        delete_class(request.args["class_id"])
    except:
        return json.dumps({"success": False}), 500
    else:
        return json.dumps({"success": True}), 200


@app.route("/delete-all-iterations", methods=["POST"])
def delete_all_iterations_endpoint():
    """
    Method(s): POST

    Take request args of the following fields:
        task_id: int

    Delete a task and all its associated iterations.
    """
    try:
        delete_all_iterations(request.args["task_id"])
    except:
        return json.dumps({"success": False}), 500
    else:
        return json.dumps({"success": True}), 200

@app.route("/delete-iteration", methods=["POST"])
def delete_iteration_endpoint():
    """
    Method(s): POST

    Take request args of the following fields:
        task_id: int
        iteration: int

    Delete a task iteration.
    """
    try:
        delete_iteration(request.args["task_id"], request.args["iteration"])
    except:
        return json.dumps({"success": False}), 500
    else:
        return json.dumps({"success": True}), 200


@app.route("/canvas-key", methods=["POST"])
def canvas_key():
    """
    Method(s): POST

    Take a form of the following fields:
        api_key: str

    Set the Canvas key for the current user.
    """
    username = CASClient().authenticate()
    api_key = request.form["api_key"]

    if validate_api_key(api_key) is False:
        return json.dumps({"success": False}), 400

    try:
        insert_canvas_key(username, api_key)
    except:
        return json.dumps({"success": False}), 500
    else:
        return json.dumps({"success": True}), 200


@app.route("/canvas-class", methods=["POST"])
def canvas_class():
    """
    Method(s): POST

    Import classes from Canvas.
    """
    username = CASClient().authenticate()
    try:
        fetch_canvas_courses(fetch_current_semester(), username)
    except:
        return json.dumps({"success": False}), 500
    else:
        return json.dumps({"success": True}), 200


@app.route("/edit-task-details", methods=["POST"])
def edit_task_details():
    """
    Method(s): POST

    Take a form of the following fields:
        task_id: int
        class_id: int
        iteration: int
        iteration_title: str
        priority: int
        link: str
        due_date: Date
        est_time: float
        notes: str
        repeat_freq: str
        repeat_end: Date

    Update the details of an existing task and/or task iteration.
    """
    username = CASClient().authenticate()
    # TODO: Potentially change class_id to class
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

    try:
        update_task_details(task_details)
    except:
        return json.dumps({"success": False}), 500
    else:
        return json.dumps({"success": True}), 200


@app.route("/edit-class-details", methods=["POST"])
def edit_class_details():
    """
    Method(s): POST

    Take a form of the following fields:
        title: str
        class_id: int
        dept: str
        num: int
        color: str

    Update the details of an existing task and/or task iteration.
    """
    username = CASClient().authenticate()
    class_details = {"title": None, "class_id": None, "dept": None, "num": None,
                "color": None, "active_status": None, "username": username}

    class_details["class_id"] = request.args["class_id"]
    for key, item in request.form.items():
        class_details[key] = item

    try:
        update_class_details(class_details)
    except:
        return json.dumps({"success": False}), 500
    else:
        return json.dumps({"success": True}), 200


@app.route("/canvas-task", methods=["POST"])
def canvas_task():
    """
    Method(s): POST

    Take a JSON list of tasks.

    Imports the given Canvas tasks.
    """
    username = CASClient().authenticate()
    task_list = []
    for value in request.form.values():
        # json.loads returns dictionary, first key is status (new or updated), second is task itself
        task_list.append(json.loads(value))

    try:
        insert_canvas_tasks(task_list, username)
    except:
        return json.dumps({"success": False}), 500
    else:
        return json.dumps({"success": True}), 200


@app.route("/group-task", methods=["POST"])
def group_tasks():
    """
    Method(s): POST

    Take a form with values being task ids.

    Group the selected tasks.
    """
    username = CASClient().authenticate()
    task_ids = []
    group_title = ""

    for value in request.form.values():
        try:
            task_id = int(value)
            task_ids.append(task_id)
        except ValueError:
            group_title = value

    try:
        create_new_group(task_ids, group_title, username)
    except:
        return json.dumps({"success": False}), 500
    else:
        return json.dumps({"success": True}), 200


@app.route("/task-details", methods=['GET'])
def task_details_endpoint():
    """
    Method(s): GET

    Take request args of the following fields:
        task_id: int
        iteration: int

    Return JSON of the given iteration's details.
    """
    username = CASClient().authenticate()
    task_id = request.args["task_id"]
    iteration = request.args["iteration"]
    task_details = fetch_task_details(task_id, iteration, username)

    # If task_details is None (which will occur if user manually inputs task_id they do not have
    # access to) then raise a 403 error
    if task_details is None:
        return json.dumps({"success": False}), 403

    return json.dumps(task_details, default=str)


@app.route("/get-graph-data", methods=["GET"])
def get_graph_data():
    """
    Method(s): GET

    Take request args of the following fields:
        task_id: int
        iteration: int

    Return JSON of the given iteration's graph data.
    """
    username = CASClient().authenticate()
    task_id = request.args["task_id"]
    iteration = request.args["iteration"]
    # Contains labels, actual_times, and predicted_times
    try:
        times = fetch_graph_times(task_id, iteration, username)
    except:
        return json.dumps({"success": False}), 500

    return json.dumps(times, default=dict)# dumps is for str formatting dict


@app.route("/class-details", methods=["GET"])
def class_details_json():
    """
    Method(s): GET

    Take request args of the following fields:
        class_id: int

    Return JSON of the given class's details.
    """
    username = CASClient().authenticate()
    class_details = fetch_class_details(request.args["class_id"], username)

    # If task_details is None (which will occur if user manually inputs task_id they do not have
    # access to) then raise a 403 error
    if class_details is None:
        return json.dumps({"success": False}), 403

    return json.dumps(class_details, default=str)


@app.route("/get-canvas-tasks", methods=["GET"])
def get_canvas_tasks():
    """
    Method(s): GET

    Return JSON of the current user's canvas tasks.
    """
    try:
        tasks = fetch_canvas_tasks(fetch_current_semester(), CASClient().authenticate())
    except:
        return json.dumps({"success": False}), 500
    return json.dumps(tasks, default=str)


@app.route("/get-classes", methods=["GET"])
def get_classes():
    """
    Method(s): GET

    Return JSON of the current user's classes.
    """
    try:
        classes = fetch_class_list(CASClient().authenticate())
    except:
        return json.dumps({"success": False}), 500
    return json.dumps(classes, default=str)


@app.route("/get-tasks", methods=["GET"])
def get_tasks():
    """
    Method(s): GET

    Fetch all tasks associated with a given class and returns information in JSON format.
    If class is left as none, return all tasks for all classes.
    """
    username = CASClient().authenticate()
    class_id = request.args["class_id"]
    try:
        tasks = fetch_tasks_from_class(class_id, username)
    except:
        return json.dumps({"success": False}), 500

    # Set null due_dates to 'Group' to avoid showing null due dates on modal
    for task in tasks:
        if task["due_date"] is None:
            task["due_date"] = "Group"
        if task["title"] is None or task["title"] == "":
            task["title"] = task["iteration_title"]

    return json.dumps(tasks, default=str)
