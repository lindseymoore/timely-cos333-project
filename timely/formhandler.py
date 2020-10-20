import models 


# Handles the creation of assignments
def assignmentHandler(details):
	assignmentDetails = models.AssignmentDetails()

	assignmentDetails.assignment_title = details['assignment_title']
	assignmentDetails.class_id = details['class_id']
	assignmentDetails.priority = details['priority']
	assignmentDetails.link = details['link']
	assignmentDetails.notes = details['notes']
	assignmentDetails.due_date = details['due_date']
	assignmentDetails.due_time = details['due_time']
	assignmentDetails.repeat_freq = details['repeat_freq']
	assignmentDetails.repeat_end = details['repeat_end']

	return assignmentDetails




