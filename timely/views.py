"""Declare application views."""

from flask import render_template, request

from timely import app, db
from timely.db_queries import fetch_task_list, fetch_class_list
from timely.formhandler import task_handler, class_handler
from timely.models import TaskDetails, TaskTime, User

# repeat_freq: freq
# class_dept: dept
# class_name: title
# estimated_time: est_time
# task_title: title

@app.route('/')
@app.route('/index')
def index():
    """Return the index page."""
    #model = User.query.filter_by(username='dlipman').first()
    #classes = fetch_class_list("dlipman")
    tasks = fetch_task_list("dlipman")
    return render_template('index.html',
                param=tasks)
                #param=model.password)

@app.route('/task_form', methods = ['GET'])
def task_form():
    """Retrieve information from the task form and insert new table entries into the database.
       Entries being inserted into tables: task, task_details, task_time, repeating_task
    """

    details = {'task_title': None, 'dept' : None, 'num': None, 'priority': None, 'estimated_time': None, 
    'link': None, 'notes': None, 'due_date': None, 'due_time': None, 'repeat_freq': None, 'repeat_end': None}

    for key, item in request.args.items():
        details[key] = item

    details['class_title'] = details['dept'] + details['num']
    #TODO Research SQLAlchemy/Postgres built in id generator
    details['class_id'] = hash(details['class_title']) 
    details['task_id'] = hash(details['task_title'])

    task_tables = task_handler(details)
    # task table entry
    task = task_tables['task']
    # TaskDetails table entry
    task_details = task_tables['task_details']
    # TaskTime table entry
    task_time = task_tables['task_time']
    # Add new table entries into database
    db.session.add(task)
    db.session.add(task_details)
    db.session.add(task_time)
    # Repeatingtask table entry
    if task_tables['repeating_task'] != None:
        repeating_task = task_tables['repeating_task']
        db.add(repeating_task)
    db.session.commit()

@app.route('/class_form', methods = ['GET'])
def class_form():
    """Retrieve information from the class form and insert new table entries into the database.
       Entries being inserted into tables: class, class_details"""
    class_details = {'class_dept': None, 'class_num': None, 'semester': None, 'color': None}

    for key, item in request.args.items():
        class_details[key] = item

    class_details['class_title'] = class_details['class_dept'] + class_details['class_num']
    #TODO Research SQLAlchemy/Postgres built in id generator
    class_details['class_id'] = hash(class_details['class_title'])

    class_tables = class_handler(class_details)
    # Class table entry
    new_class = class_tables['class']
    # ClassDetails table entry
    new_class_details = class_tables['class_details']
    # Add new table intries into database
    db.session.add(new_class)
    db.session.add(new_class_details)
    db.session.commit()




