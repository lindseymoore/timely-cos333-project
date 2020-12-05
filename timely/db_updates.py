"""Functions to update the database."""

from timely import db
from timely.models import Class, Task, TaskIteration


def mark_task_complete(task_id: int, iteration: int, username: str):
    """Update the task given by task_id as complete in the db."""
    task_iteration = db.session.query(TaskIteration).filter( \
                (TaskIteration.username == username) & \
                (TaskIteration.task_id == task_id) & \
                (TaskIteration.iteration == int(iteration))).first()

    task_iteration.completed = True
    db.session.commit()


def uncomplete_task(task_id: int, iteration: int, username: str):
    """Update the task given by task_id as complete in the db."""
    task_iteration = db.session.query(TaskIteration).filter( \
                (TaskIteration.username == username) & \
                (TaskIteration.task_id == task_id) & \
                (TaskIteration.iteration == int(iteration))).first()

    task_iteration.completed = False
    db.session.commit()


def delete_class(class_id: int):
    """Delete a class and all associated tasks."""
    db.session.query(Class).filter(Class.class_id == class_id).delete()
    db.session.query(Task).filter(Task.class_id == class_id).delete()
    db.session.query(TaskIteration).filter(TaskIteration.class_id == class_id).delete()
    db.session.commit()


def delete_all_iterations(task_id: int):
    """Delete a task and all associated instances."""
    db.session.query(Task).filter(Task.task_id == task_id).delete()
    db.session.query(TaskIteration).filter(TaskIteration.task_id == task_id).delete()
    db.session.commit()

def delete_iteration(task_id: int, iteration: int):
    """Delete a task and all associated instances."""
    db.session.query(TaskIteration).filter((TaskIteration.task_id == task_id) & \
                                            (TaskIteration.iteration == iteration)).delete()
    next_iterations = db.session.query(TaskIteration).filter((TaskIteration.task_id == task_id) & \
                                            (TaskIteration.iteration > iteration)).all()
    for i in next_iterations:
        i.iteration = i.iteration - 1
    db.session.commit()
