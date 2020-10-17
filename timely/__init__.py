"""Initialize the flask application."""

from flask import Flask, render_template

app = Flask(__name__)

# pylint: disable=wrong-import-position
import timely.views
# pylint: enable=wrong-import-position
