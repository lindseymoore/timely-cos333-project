#!/usr/bin/env python

#-----------------------------------------------------------------------
# Based on penny.py Bob Dondero
#-----------------------------------------------------------------------

"""A flask application."""

from flask import Flask, render_template


app = Flask(__name__, template_folder='.')


@app.route('/')
@app.route('/index')
def index():
    """Return the index page."""
    return render_template('index.html')
