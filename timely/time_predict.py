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
    older_time = 0
    recent_time = 0
    recent_task_weight = 0.60
    older_task_weight = 0.40
    
    older_num_completed = 0
    recent_num_completed = 0
    num_completed = 0

    weighted = 3.0 # number of most recent iterations that are given greater weight

    num_iterations = len(iteration_times)
    weighted_start = num_iterations - weighted
    print(num_iterations)

    for iteration in iteration_times:
        if num_iterations > weighted:
            if iteration["completed"] & (iteration["iteration"] <= weighted_start):
                print("not weighted:", iteration["actual_time"])
                older_time += iteration["actual_time"]
                older_num_completed += 1
            if iteration["completed"] & (iteration["iteration"] > weighted_start):
                print("weighted:", iteration["actual_time"])
                recent_time += iteration["actual_time"]
                recent_num_completed += 1

        # if there is not enough iterations for weighting to start
        else:
            if iteration["completed"]:
                recent_time += iteration["actual_time"]
                num_completed += 1


    if num_completed == 0:
        return iteration_times[0]["est_time"]
    else:
        if num_iterations > weighted:
            older_avg_time = older_time / older_num_completed
            print("older avg", older_avg_time)
            recent_avg_time = recent_time / recent_num_completed
            print("recent avg", recent_avg_time)
            weighted_time = older_avg_time * older_task_weight + recent_avg_time * recent_task_weight
        else:
            weighted_time = recent_time/num_completed
            print("regular", weighted_time)
        return weighted_time


def update_completion_time(task_id: int, iteration: int, username: str, actual_time: float):
    """
    Take task_id, iteration, and username.
    Update the actual_time it takes to complete a task upon completion for the task.
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
