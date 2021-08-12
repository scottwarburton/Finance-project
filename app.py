

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskdb.db'
db = SQLAlchemy(app)

class Stocks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False)
    units = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Decimal(7, 2), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return "<Stock %r>" % self.id

@app.route("/", methods=["POST", "GET"])
def home():
    return render_template("home.html")
"""

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<Task %r>" % self.id
        #when creating a task, will return Task then id of task created

#setup route so don't end up with 404 when searching url

@app.route("/", methods=["POST", "GET"])
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

@app.route("/delete/<int:id>")    #using id from table as unique identifier for tasks
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect("/")
    except:
        return "Error deleting task"

@app.route("/update/<int:id>", methods=["GET", "POST"])
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
"""

if __name__ == "__main__":
    app.run(debug=True)






