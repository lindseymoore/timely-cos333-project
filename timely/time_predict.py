""" Predict the time it will take user to complete a task based on previous iterations """

from typing import List
from timely import db
from timely.models import Task, TaskIteration

def fetch_task_times(task_id: str, username: str) -> List[dict]:
    """
    Given a task id and a username, the function will return a list of dictionaries, with each
    dictionary reprsenting an iteration of the task associated with the task_id. Each dictionary
    will contain a completed, est_time, actual_time, and timely_pred for the task iteration. 
    """

    iteration_times_list = []

    # How do I query the time data specificall rather than just every field in the row with the all?
    # What sql lanugauge is this/ what can I look up to find documentation for the syntax?
    times = db.session.query(Task, TaskIteration).filter((Task.username == username) &
            (Task.task_id == task_id)).join(TaskIteration, (TaskIteration.username == Task.username)
            & (TaskIteration.task_id == Task.task_id)).all()

    for (task, task_iteration) in times:
        iteration_times_obj = {"iteration": task_iteration.iteration,
                    "est_time": task_iteration.est_time, "actual_time": task_iteration.actual_time,
                    "timely_pred": task_iteration.timely_pred, 
                    "completed": task_iteration.completed}

    iteration_times_list.append(iteration_times_obj)

    return iteration_times_obj

def find_avg_prediction(iteration_times: List[dict]):
    """
    Takes in a list of dictionaries, with each dictionary represnting a task with a completed,
    est_time, actual_time, and timely_pred. Takes the average for take the actual completion time 
    of each iteration of the task and output a predicted time for the task.
    """

    index = 0
    sum = 0
    while(iteration_times[index]["completed"] == True):
        sum += iteration_times[index]["actual_time"]
        index += 1
    
    curr_iteration_time_predict = iteration_times[index]["timely_pred"] = sum/index

    return curr_iteration_time_predict
