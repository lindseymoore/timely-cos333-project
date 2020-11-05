""" Predict the time it will take user to complete a task based on previous iterations """

from typing import List
from timely import db
from timely.models import Task, TaskIteration
import sys

def fetch_task_times(task_id: str, username: str) -> List[dict]:
    """
    Given a task id and a username, the function will return a list of dictionaries, with each
    dictionary reprsenting an iteration of the task associated with the task_id. Each dictionary
    will contain a completed, est_time, actual_time, and timely_pred for the task iteration. 
    """

    iteration_times_list = []

    times = db.session.query(Task, TaskIteration).filter((Task.username == username) &
            (Task.task_id == task_id)).join(TaskIteration, (TaskIteration.username == Task.username)
            & (TaskIteration.task_id == Task.task_id)).all()

    for (task, task_iteration) in times:
        iteration_times_obj = {"iteration": task_iteration.iteration,
                    "est_time": task_iteration.est_time, "actual_time": task_iteration.actual_time,
                    "timely_pred": task_iteration.timely_pred, 
                    "completed": task_iteration.completed}

    iteration_times_list.append(iteration_times_obj)

    return iteration_times_list

def find_avg_prediction(iteration_times: List[dict]):
    """
    Takes in a list of dictionaries, with each dictionary represnting a task with a completed,
    est_time, actual_time, and timely_pred. Takes the average for take the actual completion time 
    of each iteration of the task and output a predicted time for the task.
    """

    index = 0
    sum = 0
    print(len(iteration_times))
    print(index)
    sys.stdout(index)
    while(iteration_times[index]["completed"] == True):
        sum += iteration_times[index]["actual_time"]
        index += 1
    
    curr_iteration_time_predict = iteration_times[index]["timely_pred"] = sum/(index+1)

    return curr_iteration_time_predict

def update_completion_time(task_id: int, iteration: int, username: str, actual_time: float):
    """ Takes in a task_id, iteration, username, and updates the actual_time it takes to complete 
    a task upon completion fo the task."""

    task_iteration = db.session.query(TaskIteration).filter((TaskIteration.username == username) &
                (TaskIteration.task_id == task_id) & (TaskIteration.iteration == iteration)).first()
    task_iteration.actual_time = actual_time
    db.session.commit()


def update_timely_pred(task_id: int, iteration: int, username: str):
    """ Update the timely prediction for a given by task_id as complete in the db."""
    task_iteration = db.session.query(TaskIteration).filter((TaskIteration.username == username) &
                (TaskIteration.task_id == task_id) &
                (TaskIteration.iteration == iteration)).first()
    iteration_times = fetch_task_times(task_id, username)

    next_task_iteration = db.session.query(TaskIteration).filter(
                (TaskIteration.username == username) &
                (TaskIteration.task_id == task_id) & 
                (TaskIteration.iteration == int(iteration) + 1)).first()
    next_task_iteration.timely_pred = find_avg_prediction(iteration_times)
    db.session.commit()




       

    
