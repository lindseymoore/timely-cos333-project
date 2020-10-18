"""Initialize the flask application."""

from os import environ

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = environ["DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# pylint: disable=wrong-import-position
from timely import models, views
# pylint: enable=wrong-import-position
