"""Declare application views."""

from flask import render_template

from timely import app
from timely.models import User, AssignmentDetails, AssignmentTime


@app.route('/')
@app.route('/index')
def index():
    """Return the index page."""
    model = User.query.filter_by(username='dlipman').first()
    return render_template('index.html',
                param=model.password)

@app.route('/assignmentForm', methods = ['GET'])
def assignmentForm():

	details = {'assignment_title':None, 'class_dept':None, 'class_num':None, 'priority':None, 'estimated_time':None, 
				'link':None, 'notes':None, 'due_date':None, 'due_time':None, 'repeat_freq':None, 'repeat_end':None, }

	for key, item in request.args.items():
        details[key] = item

    details['class_title'] = details['class_dept'] + details['class_num']

    details['class_id'] = hash(details['class_title'])




