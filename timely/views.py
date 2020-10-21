"""Declare application views."""

from flask import render_template

from timely import app


@app.route('/')
@app.route('/index')
def index():
    """Return the index page."""
    class_dict = {"class_name" : "Advanced Programming Techniques",
                "class_dept" : "COS",
                "class_num" : "333",
                "color" : "red"
                }
    class_2 = {"class_name" : "Intro French",
                "class_dept" : "FRN",
                "class_num" : "101",
                "color" : "purple"
                }
    class_3 = {"class_name" : "Chinese History",
                "class_dept" : "CHI",
                "class_num" : "411",
                "color" : "orange"
                }
    class_4 = {"class_name" : "Entrepreneurship",
                "class_dept" : "EGR",
                "class_num" : "893",
                "color" : "green"
                }
    assignment_dict = {"assignment_title" : "Prototype",
                "class" : "COS333",
                "priority" : "5",
                "estimated_time" : "4h",
                "link" : "https://www.cs.princeton.edu/courses/archive/fall20/cos333/project.html",
                "notes" : "This is gonna be a tough one.",
                "due_date" : "10/25/2020",
                "repeat_freq" : "",
                "repeat_ends" : ""}
        
    class_list = [class_dict, class_2, class_3, class_4]
    assignment_list = [assignment_dict]
    return render_template('index.html',
                class_list=class_list,
                assignment_list=assignment_list)
