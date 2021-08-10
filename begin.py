

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

begin = Flask(__name
begin.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///flaskdb.db"
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

@begin.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    begin.run(debug=True)

#to setup
"""
source proj/bin/activate
python3 begin.py
localhost:5000      #go to this url
"""




