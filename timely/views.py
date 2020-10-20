"""Declare application views."""

from flask import render_template

from formhandler import assignment_handler, class_handler
from timely import app, db
from timely.models import AssignmentDetails, AssignmentTime, User


@app.route('/')
@app.route('/index')
def index():
    """Return the index page."""
    model = User.query.filter_by(username='dlipman').first()
    return render_template('index.html',
                param=model.password)

@app.route('/assignment_form', methods = ['GET'])
def assignment_form():
    """Retrieve information from the assignment form and insert new table entries into the database.
       Entries being inserted into tables: assignment, assignment_details, assignment_time, repeating_assignment"""
	details = {'assignment_title': None, 'class_dept' : None, 'class_num': None, 'priority': None, 'estimated_time': None, 
				'link': None, 'notes': None, 'due_date': None, 'due_time': None, 'repeat_freq': None, 'repeat_end': None, }

	for key, item in request.args.items():
        details[key] = item

    details['class_title'] = details['class_dept'] + details['class_num']
    #TODO Research SQLAlchemy/Postgres built in id generator
    details['class_id'] = hash(details['class_title']) 
    details['assignemnt_id'] = hash(details['assignment_title'])

    assignment_tables = assignment_handler(details)
    # Assignment table entry
    assignment = assignment_tables['assignment']
    # AssignmentDetails table entry
    assignment_details = assignment_tables['assignment_details']
    # AssignmentTime table entry
    assignment_time = assignment_tables['assignment_time']
    # Add new table entries into database
    db.session.add(assignment)
    db.session.add(assignment_details)
    db.session.add(assignment_time)
    # RepeatingAssignment table entry
    if assignment_tables['repeating_assignment'] != None:
        repeating_assignment = assignment_tables['repeating_assignment']
        db.add(repeating_assignment)
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




