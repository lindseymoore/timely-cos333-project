"""Functions to parse information from Canvas, fetch classes and tasks, and insert as new entries
in the database."""

from datetime import datetime
import random

from canvasapi import Canvas

from timely import db
from timely.db_queries import (get_class_id, get_next_task_iteration,
                               get_task_id)
from timely.models import Class, Task, TaskIteration

API_URL = "https://princeton.instructure.com"
API_KEY = "12465~RpGmbRqf0075STEfJkuwt72NzzYs5Zv1dglYd5vIPKqEtkrF2EztidbzCRLg8cFy"
canvas = Canvas(API_URL, API_KEY)


def fetch_canvas_courses(curr_semester: str, username: str):
    """
    Function to fetch classes a specific user is enrolled in on Canvas and add those classes
    to the database. Fetches classes a user is currently enrolled in given by string curr_semester,
    which is denoted F2020 for fall 2020, S2021 for spring 2021, etc.
    """
    #username = CASClient().authenticate()
    classes = []

    for course in canvas.get_courses():
        term = course.course_code[-5:]
        if term == curr_semester:
            new_class = Class(username = username, active_status = True)
          
            # find and insert course title
            name_idx = course.name.find(curr_semester) + len(curr_semester) + 1
            new_class.title = course.name[name_idx:]

            # find and insert dept and num
            new_class.dept = course.course_code[:3]
            new_class.num = int(course.course_code[3:6])

            #TODO implement edit class button to change the color afterwards
            new_class.color = random.choice(['red', 'green', 'purple', 'orange'])

            classes.append(new_class)

    for course in classes:
        db.session.add(course)

    db.session.commit()


def fetch_canvas_tasks(curr_semester: str, username: str):
    """
    Function to fetch upcoming tasks a specific user has on Canvas and add those classes
    to the database. Fetches classes a user is currently enrolled in given by string curr_semester,
    which is denoted F2020 for fall 2020, S2021 for spring 2021, etc. Fetches all active tasks 
    (tasks due after the current date) for each class.
    """

    for course in canvas.get_courses():
        term = course.course_code[-5:]
        if term == curr_semester:
            name_idx = course.name.find(curr_semester) + len(curr_semester) + 1
            course_title = course.name[name_idx:]
            class_id = get_class_id(course_title)

            # TODO figure out if a task from Canvas is repeating or not, defaulting to false
            for assignment in course.get_assignments():
                if assignment.due_at is None:
                    continue

                task = Task(username = username, class_id = class_id, title = assignment.name,
                    repeat = False)

                db.session.add(task)
                db.session.commit()

                task_iteration = TaskIteration(username = username, class_id = class_id,
                    task_id = get_task_id(task.title, class_id))
               
                task_iteration.iteration = get_next_task_iteration(task_iteration.task_id)
                task_iteration.link = assignment.html_url

                datetime_due = assignment.due_at.split('T')
                due_date = datetime.strptime(datetime_due[0], '%Y-%m-%d')
                due_time = datetime.strptime(datetime_due[1][:-1], '%H:%M:%S')

                task_iteration.due_date = due_date
                task_iteration.due_time = due_time

                if task_iteration.due_date < datetime.today():
                    task_iteration.completed = True
                else:
                    task_iteration.completed = False
                # else:
                #     task_iteration.due_date = None
                #     task_iteration.due_time = None
                #     task_iteration.completed = False

                db.session.add(task_iteration)
                db.session.commit()
