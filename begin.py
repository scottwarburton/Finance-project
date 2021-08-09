

from flask import Flask, render_template

begin = Flask(__name__)

#setup route so don't end up with 404 when searching url

@begin.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    begin.run(debug=True)

#to run
"""
python3 begin.py
url
localhost:5000
"""




