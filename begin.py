

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

begin = Flask(__name__)
begin.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskdb.db'
db = SQLAlchemy(begin)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<Task %r>" % self.id
        #when creating a task, will return Task then id of task created

#setup route so don't end up with 404 when searching url

@begin.route("/", methods=["POST", "GET"])

def index():
    if request.method == "POST":
        task_content = request.form["content"]  #create new task from input (html id)
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)    #add to our database
            db.session.commit()
            return redirect("/") #then redirect back to our index page
        except:
            return "Error adding task"

        #when pressing submit button
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()    #ordering by newest to oldest (could do .first())
        return render_template("index.html", tasks=tasks)   #
        #when loading page

@begin.route("/delete/<int:id>")    #using id from table as unique identifier for tasks

def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect("/")
    except:
        return "Error deleting task"

@begin.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == "POST":
        task.content = request.form["content"]

        try:
            db.session.commit()
            return redirect("/")
        except:
            return "Error updating task"
    else:
        return render_template("update.html", task=task)


if __name__ == "__main__":
    begin.run(debug=True)

#to setup
"""
source proj/bin/activate
python3 begin.py
localhost:5000      #go to this url
"""




