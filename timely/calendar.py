"""Functions for the calendar view."""

from datetime import date, datetime, timedelta


def fetch_curr_week():
    """
    Fetches the current week based on today's date. Returns the week (from Sunday to Saturday) that
    today's date is a part of as a dictionary of weekdays (as date formatted strings).
    """
    curr_date = date.today()
    offset = curr_date.weekday() #where 0 is monday

    #Determine what date corresponds to Sunday
    increment = timedelta(days=offset+1)
    day = curr_date - increment #initially sunday

    if offset == 6:  # If current date is Sunday
        day = curr_date

    #Create a dict of dates based on the sunday
    week = {}
    for ii in range(0, 7):
        week[ii] = day.strftime("%m/%d/%y")
        day += timedelta(days=1)

    return week


def fetch_week(week_dates: str, prev: bool):
    """
    Fetches a week based on a provided Sunday's date (week_dates). If prev is True, returns the
    week preceding the given Sunday. Otherwise fetches the week following the given Sunday. Returns
    the associated dictionary of weekdays (as date formatted strings).
    """
    curr_sunday = week_dates
    sunday = datetime.strptime(curr_sunday, '%m/%d/%y')

    #Determine what date corresponds to prev or next Sunday
    if prev:
        day = sunday - timedelta(days=7)
    else:
        day = sunday + timedelta(days=7)

    #Create a dict of dates based on the sunday
    week = {}
    for ii in range(0, 7):
        week[ii] = day.strftime("%m/%d/%y")
        day += timedelta(days=1)

    return week
