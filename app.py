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
    price = db.Column(db.Numeric(9, 2))
    daily_return = db.Column(db.Numeric(9, 4))
    beta = db.Column(db.Numeric(9, 2))
    mcap = db.Column(db.String(10))
    pe = db.Column(db.Numeric(9, 2))
    low52 = db.Column(db.Numeric(9, 2))
    high52 = db.Column(db.Numeric(9, 2))
    def __repr__(self):
        return "<Current %r>" % self.id


def find_stock():
    url = "https://finance.yahoo.com/quote/" + str(request.form["ticker-search"])
    if not requests.get(url).status_code:
        return "Invalid stock ticker"
    else:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "lxml")
        stock_price = float(soup.find("span", {"class": "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text.replace(",", ""))
        prev_price = float(soup.find("div", {"data-test": "left-summary-table"}).find("table").find("tbody").find_all("tr")[0].find_all("td")[
            1].text.replace(",",""))
        stock_daily_return = stock_price / prev_price - 1
        stock_beta = float(soup.find("div", {"data-test": "right-summary-table"}).find("table").find("tbody").find_all("tr")[1].find_all(
            "td")[1].find("span").text.replace(",",""))
        stock_mcap = soup.find("div", {"data-test": "right-summary-table"}).find("table").find("tbody").find_all("tr")[0].find_all(
            "td")[1].find("span").text
        stock_pe = float(soup.find("div", {"data-test": "right-summary-table"}).find("table").find("tbody").find_all("tr")[2].find_all(
            "td")[1].find("span").text.replace(",",""))
        range = soup.find("div", {"data-test": "left-summary-table"}).find("table").find("tbody").find_all("tr")[5].find_all(
            "td")[1].text
        low52 = float(range.split("-")[0].rstrip().replace(",",""))
        high52 = float(range.split("-")[1].lstrip().replace(",",""))
        return [stock_price, stock_daily_return, stock_beta, stock_mcap, stock_pe, low52, high52]


@app.route("/", methods=["POST", "GET"])
def dashboard():
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
                                 daily_return=str(stock_stats[1]), beta=str(stock_stats[2]), mcap=str(stock_stats[3]),
                                 pe=str(stock_stats[4]), low52=str(stock_stats[5]), high52=str(stock_stats[6]))
            try:
                db.session.add(new_search)
                db.session.commit()
                return redirect("/")
            except:
                return "Error searching stock"
    else:
        stocks = Stocks.query.all()
        current = Current.query.order_by(Current.id.desc()).all()
        return render_template("dashboard.html", stocks=stocks, current=current)

@app.route("/analysis")
def analysis():
    return render_template("analysis.html")

@app.route("/project")
def project():
    return render_template("project.html")

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
