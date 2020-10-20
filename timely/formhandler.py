import models 


# Handles the creation of assignments for input into "assignment" table
def assignment_handler(details: dict):
	'''Takes details dictionary (user inputted fields in assignment form) as input.  
	   Returns a dictionary of Assignment, AssignmentDetails, AssignmentTime, and RepeatingAssignment
	   classes to be inputted into the database as tables. '''
	assignment = models.Assignment()
	assignment_details = models.AssignmentDetails()
	assignment_time = models.AssignmentTime()
	repeating_assigment = None

	# Inser into Assignment table
	assignment.username = 'Princeton Student' # TODO UPDATE TO USE CAS AUTHENTICATION
	assignment.assignment_id = details['assignment_id']
	assignment.class_id = details['class_id']
	assignment.assignment_title = details['assignment_title']
	if details['repeat_freq'] != None:
		assignment.repeat = True
	else:
		assignment.repeat = False

	# Insert into AssignmentDetails table
	assignment_details.username = 'Princeton Student' # TODO UPDATE TO USE CAS AUTHENTICATION
	assignment_details.assignment_id = details['assignment_id']
	assignment_details.class_id = details['class_id']
	assignment_details.assignment_iteration = 1 #TODO UPDATE COUNTER OF ASSIGNMENT ITERATIONS
	assignment_details.priority = details['priority']
	assignment_details.link = details['link']
	assignment_details.due_date = details['due_date']
	assignment_details.due_time = details['due_time']
	assignment.notes = details['notes']

	# Insert into AssignmentTime table
	assignment_time.username = 'Princeton Student' # TODO UPDATE TO USE CAS AUTHENTICATION
	assignment_time.assignment_id = details['assignment_id']
	assignment_time.class_id = details['class_id']
	assignment_time.assignment_iteration = 1 #TODO UPDATE COUNTER OF ASSIGNMENT ITERATIONS
	assignment_time.estimated_time = details['estimated_time']
	assignment_time.actual_time = None
	assignment_time.timely_prediction = None

	# If assignment is repeating, create RepeatingAssignments table
	if details['repeat_freq'] != None:
		repeating_assigment = models.RepeatingAssignment()
		repeating_assigment.username = 'Princeton Student' # TODO UPDATE TO USE CAS AUTHENTICATION
		repeating_assigment.assignment_id = details['assignment_id']
		repeating_assigment.class_id = details['class_id']
		repeating_assigment.repeat_freq = details['repeat_freq']
		repeating_assigment.repeat_end = details['repeat_end']

	tables = {'assignment': assignment, 'assignment_details': assignment_details, 'assignment_time': assignment_time, 'repeating_assignment': repeating_assigment}

	return tables


# Handler function to deal with the creation of classes for input into "class" table
def class_handler(class_details: dict):
	new_class = models.Class()
	class_details = models.ClassDetails()

	# Insert into class table
	new_class.class_id = class_details['class_id']
	new_class.class_title = class_details['class_title']

	# Insert into class_details table
	class_details.class_id = class_details['class_id']
	class_details.username = 'Princeton Student'  # TODO UPDATE TO USE CAS AUTHENTICATION
	class_details.active_status = True
	class_details.color = class_details['color']
