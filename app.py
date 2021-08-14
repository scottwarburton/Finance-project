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
    price = db.Column(db.Numeric(9, 2), nullable=False)
    total = db.Column(db.Numeric(9, 2))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<Stock %r>" % self.id


class Current(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10))
    price = db.Column(db.String(10))
    pe = db.Column(db.String(10))
    beta = db.Column(db.String(10))
    mcap = db.Column(db.String(10))
    pm = db.Column(db.String(10))
    de = db.Column(db.String(10))
    cur = db.Column(db.String(10))
    def __repr__(self):
        return "<Current %r>" % self.id


def find_stock():
    url = "https://finance.yahoo.com/quote/" + str(request.form["ticker-search"]) + "/key-statistics"
    if not requests.get(url).status_code:
        return "Invalid stock ticker"
    else:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "lxml")
        stock_price = soup.find_all("span", {"class": "Trsdu(0.3s)"})[18]
        stock_pe = soup.find_all("span", {"class": "Trsdu(0.3s)"})[28]
        stock_beta = soup.find_all("td", {"class": "Fw(500) Ta(end) Pstart(10px) Miw(60px)"})[4]
        stock_mcap = soup.find_all("td", {"class": "Fw(500) Ta(end) Pstart(10px) Miw(60px)"})[0]
        stock_pm = soup.find_all("td", {"class": "Fw(500) Ta(end) Pstart(10px) Miw(60px)"})[1]
        stock_de = soup.find_all("td", {"class": "Fw(500) Ta(end) Pstart(10px) Miw(60px)"})[2]
        stock_cur = soup.find_all("td", {"class": "Fw(500) Ta(end) Pstart(10px) Miw(60px)"})[3]
        return [stock_price, stock_pe, stock_beta, stock_mcap, stock_pm, stock_de, stock_cur]


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        if request.form.get("submit-add"):
            new_stock = Stocks(ticker=request.form["ticker"], units=request.form["units"],
                               price=request.form["price"],
                               total=(int(request.form["units"]) * float(request.form["price"])))
            try:
                db.session.add(new_stock)
                db.session.commit()
                return redirect("/")
            except:
                return "Error adding stock"
        elif request.form.get("submit-search"):
            stock_stats = find_stock()
            new_search = Current(ticker=request.form["ticker-search"], price=str(stock_stats[0]),
                                 pe=str(stock_stats[1]), beta=str(stock_stats[2]), mcap=str(stock_stats[3]),
                                 pm=str(stock_stats[4]), de=str(stock_stats[5]), cur=str(stock_stats[6]))
            try:
                db.session.add(new_search)
                db.session.commit()
                return redirect("/")
            except:
                return "Error searching stock"
    else:
        stocks = Stocks.query.all()
        current = Current.query.order_by(Current.id.desc()).first()
        return render_template("index.html", stocks=stocks, current=current)


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
