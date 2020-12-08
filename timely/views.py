"""Declare views (endpoints that deliver HTML)."""

from flask import redirect, render_template, request

from timely import app
from timely.calendar import fetch_curr_week, fetch_week
from timely.cas_client import CASClient
from timely.db_queries import (fetch_available_colors, fetch_class_list,
                               fetch_task_calendar_view, fetch_task_list_view,
                               fetch_user)

# NOTE: To run the application locally with CAS authentication, check out:
# "https://stackoverflow.com/questions/50236117/"
# It may be necessary to install certificates


@app.route("/")
@app.route("/landing")
def landing():
    """Return the landing page."""
    # Redirects to list if user is logged in
    try:
        CASClient().authenticate()
    except:
        return render_template("views/landing.html")
    else:
        return redirect("/list")


@app.route("/list")
def list_view():
    """Return the index page."""
    username = CASClient().authenticate()
    if "sort" in request.args:
        sort = request.args['sort']
    else:
        sort = "due_date"

    classes = fetch_class_list(username)
    tasks = fetch_task_list_view(username, sort)
    user = fetch_user(username)
    colors = fetch_available_colors(username)
    return render_template("views/list.html",
                class_list=classes,
                task_list=tasks,
                user_info = user,
                colors = colors)


@app.route("/calendar")
def calendar():
    """Return the calendar page."""
    username = CASClient().authenticate()
    classes = fetch_class_list(username)
    tasks = fetch_task_calendar_view(username)
    week_dates = fetch_curr_week()
    return render_template("views/calendar.html",
                class_list=classes,
                task_list=tasks,
                week_dates=week_dates)


@app.route("/calendar/next_week")
def next_week():
    """Return the next week of the calendar page."""
    username = CASClient().authenticate()
    classes = fetch_class_list(username)
    tasks = fetch_task_calendar_view(username)
    week_dates = request.args["week-dates"]
    next_week_dates = fetch_week(week_dates, False)
    return render_template("views/calendar.html",
                class_list=classes,
                task_list=tasks,
                week_dates=next_week_dates)


@app.route("/calendar/prev_week")
def prev_week():
    """Return the previous week of the calendar page."""
    username = CASClient().authenticate()
    classes = fetch_class_list(username)
    tasks = fetch_task_calendar_view(username)
    week_dates = request.args["week-dates"]
    # week_dates = eval(week_dates)
    prev_week_dates = fetch_week(week_dates, True)
    return render_template("views/calendar.html",
                class_list=classes,
                task_list=tasks,
                week_dates=prev_week_dates)


@app.route("/about")
def about():
    """Display about page."""
    try:
        CASClient().authenticate()
    except:
        return render_template("views/about.html", public=True)
    else:
        return render_template("views/about.html", public=False)


@app.route("/feedback")
def feedback():
    """Display the feedback page."""
    try:
        CASClient().authenticate()
    except:
        return render_template("views/feedback.html", public=True)
    else:
        return render_template("views/feedback.html", public=False)


@app.route('/logout', methods=['GET'])
def logout():
    """Log the user out of the application."""
    cas_client = CASClient()
    cas_client.authenticate()
    cas_client.logout()


@app.errorhandler(403)
@app.route("/403")
def forbidden(e=None):
    """Return the 403 page."""
    return render_template("views/403.html"), 403


@app.errorhandler(404)
def page_not_found(e=None):
    """Return the 404 page."""
    return render_template("views/404.html"), 404


@app.errorhandler(500)
def server_error(e=None):
    """Return the 500 page."""
    return render_template("views/500.html"), 404
