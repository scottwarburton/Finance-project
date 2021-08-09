

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

begin = Flask(__name__)

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




