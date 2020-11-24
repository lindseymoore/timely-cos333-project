""" Predict the time it will take user to complete a task based on previous iterations """

from typing import List

from timely import db
from timely.models import TaskIteration


def fetch_task_times(task_id: str, username: str) -> List[dict]:
    """
    Take a task id and a username.
    Return a list of dicts representing all task iterations of task_id with keys:
        iteration
        est_time
        actual_time
        timely_pred
        completed
    """
    query_result = db.session.query(TaskIteration).filter( \
                (TaskIteration.username == username) & \
                (TaskIteration.task_id == task_id)).all()

    times = []
    for iteration in query_result:
        times.append({"iteration": iteration.iteration,
            "est_time": iteration.est_time, "actual_time": iteration.actual_time,
            "timely_pred": iteration.timely_pred, "completed": iteration.completed})

    # Logging output
    print("Fetched iterations for TASK_ID=" + task_id + " & USERNAME=" + username[:-1] + ":")
    for iteration in times:
        print(iteration)

    return times


def find_avg_prediction(iteration_times: List[dict]) -> float:
    """
    Take a list of dicts representing task iterations with keys:
        est_time
        actual_time
        timely_pred
    Return a predicted time for the task.
    """
    total_time = 0
    num_completed = 0

    for iteration in iteration_times:
        if iteration["completed"]:
            total_time += iteration["actual_time"]
            num_completed += 1

    if num_completed == 0:
        return iteration_times[0]["est_time"]
    else:
        return total_time / num_completed


def update_completion_time(task_id: int, iteration: int, username: str, actual_time: float):
    """
    Take task_id, iteration, and username.
    Update the actual_time it takes to complete a task upon completion fo the task.
    """
    task_iteration = db.session.query(TaskIteration).filter( \
                (TaskIteration.username == username) & (TaskIteration.task_id == task_id) & \
                (TaskIteration.iteration == iteration)).first()
    task_iteration.actual_time = actual_time
    db.session.commit()


def update_timely_pred(task_id: int, iteration: int, username: str):
    """
    Take task_id, iteration, and username.
    If the task has another iteration, update the timely prediction for the subsequent iteration
    with a newly calculated value.
    Else, do nothing.
    """
    times = fetch_task_times(task_id, username)

    next_iteration = db.session.query(TaskIteration).filter( \
                (TaskIteration.username == username) & \
                (TaskIteration.task_id == task_id) & \
                (TaskIteration.iteration == int(iteration) + 1)).first()

    if next_iteration is not None:
        next_iteration.timely_pred = find_avg_prediction(times)
        db.session.commit()

def fetch_graph_times(task_id: int, iteration: int, username: str):
    prev_iterations = db.session.query(TaskIteration).filter( \
                (TaskIteration.username == username) & \
                (TaskIteration.task_id == task_id) & \
                (TaskIteration.completed == True) & \
                (TaskIteration.iteration < iteration)).all()
    actual_times = []       
    predicted_times = []

    for prev in prev_iterations:
        actual_times.append(prev.actual_time)
        predicted_times.append(prev.timely_pred)

    times = {"actual_times": actual_times, "predicted_times": predicted_times}

    
    return times



