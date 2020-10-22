"""Declare application views."""

from flask import render_template, request

from timely import app, db
from timely.db_queries import fetch_task_list, fetch_class_list
from timely.formhandler import task_handler, class_handler
from timely.models import TaskDetails, TaskTime, User


@app.route('/')
@app.route('/index')
def index():
    """Return the index page."""
    #model = User.query.filter_by(username='dlipman').first()
    classes = fetch_class_list("dlipman")
    #tasks = fetch_task_list("dlipman")
    return render_template('index.html',
                param=classes)
                #param=model.password)

@app.route('/task_form', methods = ['GET'])
def task_form():
    """Retrieve information from the task form and insert new table entries into the database.
       Entries being inserted into tables: task, task_details, task_time, repeating_task.
    """

    details = {'task_title': None, 'dept' : None, 'num': None, 'priority': None, 'estimated_time': None, 
    'link': None, 'notes': None, 'due_date': None, 'due_time': None, 'repeat_freq': None, 'repeat_end': None}

    for key, item in request.args.items():
        details[key] = item

    details['class_title'] = details['dept'] + details['num']

    task_handler(details)

@app.route('/class_form', methods = ['GET'])
def class_form():
    """Retrieve information from the class form and insert new table entries into the database.
       Entries being inserted into tables: class, class_details."""
    class_details = {'dept': None, 'num': None, 'semester': None, 'color': None}

    for key, item in request.args.items():
        class_details[key] = item

    class_details['class_title'] = class_details['dept'] + class_details['num']

    class_handler(class_details)
 