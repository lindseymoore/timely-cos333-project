"""Declare application views."""

from flask import render_template

from timely import app


@app.route('/')
@app.route('/index')
def index():
    """Return the index page."""
    return render_template('index.html')
