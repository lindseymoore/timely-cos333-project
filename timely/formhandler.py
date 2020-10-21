from timely.models import (Task, TaskDetails, TaskTime,
                           Class, ClassDetails, Repeatingtask)


# Handles the creation of tasks for input into "Task" table
def task_handler(details: dict) -> dict:
    '''
    Takes details dictionary (user inputted fields in new Task form) as input.  
    Returns a dictionary of Task, TaskDetails, TaskTime, and RepeatingTask
    classes to be inputted into the database as tables. 
    '''
    task = Task()
    task_details = TaskDetails()
    task_time = TaskTime()
    repeating_task = None

    # Insert into task table
    task.username = 'Princeton Student' # TODO UPDATE TO USE CAS AUTHENTICATION
    task.task_id = details['task_id']
    task.class_id = details['class_id']
    task.title = details['task_title']
    if details['repeat_freq'] != None:
        task.repeat = True
    else:
        task.repeat = False
    task.completed = False

    # Insert into taskDetails table
    task_details.username = 'Princeton Student' # TODO UPDATE TO USE CAS AUTHENTICATION
    task_details.task_id = details['task_id']
    task_details.class_id = details['class_id']
    task_details.iteration = 1 #TODO UPDATE COUNTER OF task ITERATIONS
    task_details.priority = details['priority']
    task_details.link = details['link']
    task_details.due_date = details['due_date']
    task_details.due_time = details['due_time']
    task.notes = details['notes']

    # Insert into taskTime table
    task_time.username = 'Princeton Student' # TODO UPDATE TO USE CAS AUTHENTICATION
    task_time.task_id = details['task_id']
    task_time.class_id = details['class_id']
    task_time.iteration = 1 #TODO UPDATE COUNTER OF task ITERATIONS
    task_time.estimated_time = details['estimated_time']
    task_time.actual_time = None
    task_time.timely_prediction = None

    # If task is repeating, create RepeatingTasks table
    if details['repeat_freq'] != None:
        repeating_assigment = RepeatingTask()
        repeating_assigment.username = 'Princeton Student' # TODO UPDATE TO USE CAS AUTHENTICATION
        repeating_assigment.task_id = details['task_id']
        repeating_assigment.class_id = details['class_id']
        repeating_assigment.repeat_freq = details['repeat_freq']
        repeating_assigment.repeat_end = details['repeat_end']

    task_tables = {'task': task, 'task_details': task_details, 'task_time': task_time, 'repeating_task': repeating_assigment}

    return task_tables


# Handler function to deal with the creation of classes for input into "class" table
def class_handler(class_details: dict) -> dict:
    '''
    Takes class_details dictionary (user inputted fields in new class form) as input.  
    Returns a dictionary of Class, and ClassDetails classes to be inputted into the database as tables. 
    '''
    new_class = Class()
    details = ClassDetails()

    # Insert into class table
    new_class.class_id = class_details['class_id']
    new_class.title = class_details['class_title']

    # Insert into class_details table
    details.class_id = class_details['class_id']
    details.username = 'Princeton Student'  # TODO UPDATE TO USE CAS AUTHENTICATION
    details.active_status = True
    details.color = class_details['color']

    class_tables = {'class': new_class, 'class_details': details}
    
    return class_tables
