from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskdb.db'
db = SQLAlchemy(app)

class Stocks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False)
    units = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(9,2), nullable=False)
    total = db.Column(db.Numeric(9,2))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return "<Stock %r>" % self.id

def find_stock(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "lxml")
    return soup.find("span", {"class": "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"})

def page_check():
    url = "https://finance.yahoo.com/quote/" + str(request.form["ticker_input"])
    if not requests.get(url).status_code:
        print("Invalid stock ticker")
    else:
        find_stock(url)

@app.route("/", methods=["POST", "GET"])
def index():
    current_price = "-"
    if request.method == "POST":
        if request.form.get("submit-add"):
            new_stock = Stocks(ticker=request.form["ticker"], units=request.form["units"],
                               price=request.form["price"], total=(int(request.form["units"]) * float(request.form["price"])))
            try:
                db.session.add(new_stock)
                db.session.commit()
                return redirect("/")
            except:
                return "Error adding stock"
        elif request.form.get("submit-search"):
            current_price = page_check()
    else:
        stocks = Stocks.query.all()
        return render_template("index.html", stocks=stocks, current_price=current_price)

@app.route("/delete/<int:id>")
def delete(id):
    stock_to_delete = Stocks.query.get_or_404(id)
    try:
        db.session.delete(stock_to_delete)
        db.session.commit()
        return redirect("/")
    except:
        return "Error deleting stock"

@app.route("/update/<int:id>", methods=["POST", "GET"])
def update(id):
    stock = Stocks.query.get_or_404(id)
    if request.method == "POST":
        stock.units = request.form["units"]
        stock.price = request.form["price"]
        stock.total = int(request.form["units"]) * float(request.form["price"])
        try:
            db.session.commit()
            return redirect("/")
        except:
            return "Error updating stock"
    else:
        return render_template("update.html", stock=stock)


if __name__ == "__main__":
    app.run(debug=True, threaded=True)






