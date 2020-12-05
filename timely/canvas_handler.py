"""Functions to parse information from Canvas, fetch classes and tasks, and insert as new entries
in the database."""

import random
from datetime import datetime

from canvasapi import Canvas

from timely import db
from timely.db_queries import (canvas_task_in_db, classes_from_canvas,
                               fetch_available_colors, get_api_key,
                               get_class_color, get_class_id_canvas,
                               get_class_title)
from timely.models import Class

API_URL = "https://princeton.instructure.com"


def fetch_canvas_courses(curr_semester: str, username: str):
    """
    Function to fetch classes a specific user is enrolled in on Canvas and add those classes
    to the database. Fetches classes a user is currently enrolled in given by string curr_semester,
    which is denoted F2020 for fall 2020, S2021 for spring 2021, etc.
    """
    api_key = get_api_key(username)
    canvas = Canvas(API_URL, api_key)
    classes = []
    colors = fetch_available_colors(username)
    current_canvas_classes = classes_from_canvas(username) # Classes from Canvas already in db

    for course in canvas.get_courses():
        # Check if this course is already in the db
        if course.id in current_canvas_classes:
            continue

        term = course.course_code[-5:]
        if term == curr_semester:
            new_class = Class(username = username, active_status = True)
          
            # find and insert course title
            name_idx = course.name.find(curr_semester) + len(curr_semester) + 1
            new_class.title = course.name[name_idx:]

            # find and insert dept and num
            new_class.dept = course.course_code[:3]
            new_class.num = int(course.course_code[3:6])

            if len(colors) > 0:
                new_class.color = random.choice(colors)
                colors.pop(colors.index(new_class.color))
            else:
                new_class.color = 'red'

            new_class.canvas_id = course.id

            classes.append(new_class)

    for course in classes:
        db.session.add(course)

    db.session.commit()


def fetch_canvas_tasks(curr_semester: str, username: str):
    """
    Function to fetch upcoming tasks a specific user has on Canvas and returns a list of 
    dictionaries containing information about those tasks in JSON format to be used by the Canvas 
    import modal. Fetches classes a user is currently enrolled in given by string curr_semester, 
    which is denoted F2020 for fall 2020, S2021 for spring 2021, etc. Fetches all active tasks 
    (tasks due after the current date) for each class.
    """
    api_key = get_api_key(username)
    canvas = Canvas(API_URL, api_key)

    new_tasks = []
    updated_tasks = []

    for course in canvas.get_courses():
        term = course.course_code[-5:]
        if term == curr_semester:
            canvas_class_id = course.id
            class_id = get_class_id_canvas(canvas_class_id, username)

            for assignment in course.get_assignments():
                if assignment.due_at is None:
                    continue

                canvas_task_id = assignment.id

                datetime_due = assignment.due_at.split('T')
                due_date = datetime.strptime(datetime_due[0], '%Y-%m-%d')
                completed = False

                if due_date < datetime.today():
                    completed = True

                class_color = get_class_color(class_id)
                class_title = get_class_title(class_id)

                task_info = {"title": assignment.name, "class_id": class_id, 
                    "due_date": datetime.strftime(due_date, '%Y-%m-%d'),
                    "link": assignment.html_url, "canvas_task_id": canvas_task_id,
                    "completed": completed, "class_title": class_title, "color": class_color}

                # Check if exact task is in the DB already, whether it's been updated, or whether
                # it's new
                task_in_db = canvas_task_in_db(canvas_task_id, username)
                if task_in_db[0] is False:
                    # set priority to 1 by default for new Canvas tasks
                    task_info["priority"] = 1
                    new_tasks.append(task_info)
                else:
                    current_task = task_in_db[1]
                    if current_task["due_date"] != due_date.date() \
                       or current_task["link"] != task_info["link"] \
                       or current_task["title"] != task_info["title"]:
                        updated_tasks.append(task_info)

    new_tasks = sorted(new_tasks, key = lambda task: task["due_date"], reverse=True)
    updated_tasks = sorted(updated_tasks, key = lambda task: task["due_date"], reverse=True)
    all_tasks = {"new": new_tasks, "updated": updated_tasks}
    return all_tasks
