"""Declare application views."""

from flask import render_template

from timely import app
from timely.models import User


@app.route('/')
@app.route('/index')
def index():
    """Return the index page."""
    model = User.query.filter_by(username='dlipman').first()
    return render_template('index.html',
                param=model.password)
