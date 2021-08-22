from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import requests
from bs4 import BeautifulSoup


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskdb.db'
db = SQLAlchemy(app)


class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    units = db.Column(db.Integer, nullable=False)
    purPrice = db.Column(db.Numeric(9, 2), nullable=False)
    curPrice = db.Column(db.Numeric(9, 2), nullable=False)
    purTotal = db.Column(db.Numeric(9, 2), nullable=False)
    curTotal = db.Column(db.Numeric(9, 2), nullable=False)
    pl = db.Column(db.Numeric(9, 2), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<Portfolio %r>" % self.id


class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10))
    name = db.Column(db.String(20))
    price = db.Column(db.Numeric(9, 2))
    daily_return = db.Column(db.Numeric(9, 4))
    beta = db.Column(db.Numeric(9, 2))
    mcap = db.Column(db.String(10))
    pe = db.Column(db.Numeric(9, 2))
    low52 = db.Column(db.Numeric(9, 2))
    high52 = db.Column(db.Numeric(9, 2))
    def __repr__(self):
        return "<Stock %r>" % self.id


def find_stock():
    url = "https://finance.yahoo.com/quote/" + str(request.form["ticker-search"])
    if not requests.get(url).status_code:
        return "Invalid stock ticker"
    else:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "lxml")
        stock_name = soup.find("div", {"class": "D(ib) Mt(-5px) Mend(20px) Maw(56%)--tab768 Maw(52%) Ov(h) smartphone_Maw(85%) smartphone_Mend(0px)"}).find_all(
            "div")[0].find("h1").text
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
        return [stock_name, stock_price, stock_daily_return, stock_beta, stock_mcap, stock_pe, low52, high52]

def updatePL():
    #get current stock price
    stocks = Portfolio.query.all()
    for stock in stocks:
        """get current stock price"""
        url = "https://finance.yahoo.com/quote/" + str(stock.ticker)
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "lxml")
        stock_price = float(soup.find("span", {"class": "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text.replace(",", ""))
        """update curPrice, curTotal, PL in table"""
        stock.curPrice = stock_price
        stock.curTotal = stock.units * stock_price
        stock.pl = float(stock.curTotal) - float(stock.purTotal)
        db.session.commit()

@app.route("/", methods=["POST", "GET"])
def dashboard():
    if request.method == "POST":
        ticker = Stock.query.order_by(Stock.id.desc()).first().ticker
        price = Stock.query.order_by(Stock.id.desc()).first().price
        name = Stock.query.order_by(Stock.id.desc()).first().name
        units = request.form["units"]
        new_stock = Portfolio(ticker=ticker, name=name, units=units,
                              purPrice=price, curPrice=price,
                              purTotal=(int(units) * float(price)),
                              curTotal=(int(units) * float(price)), pl=0)
        try:
            db.session.add(new_stock)
            db.session.commit()
            return redirect("/")
        except:
            return "Error adding stock"
    else:
        updatePL()
        stocks = Portfolio.query.all()
        portfolio_value = 0
        portfolio_PL = 0
        for stock in stocks:
            portfolio_value += stock.curTotal
            portfolio_PL += stock.pl
        return render_template("dashboard.html", stocks=stocks, portfolioValue=portfolio_value, portfolioPL=portfolio_PL)

@app.route("/analysis", methods=["POST", "GET"])
def analysis():
    if request.method == "POST":
        stock_stats = find_stock()
        new_search = Stock(ticker=request.form["ticker-search"], name=str(stock_stats[0]), price=str(stock_stats[1]),
                           daily_return=str(stock_stats[2]), beta=str(stock_stats[3]), mcap=str(stock_stats[4]),
                           pe=str(stock_stats[5]), low52=str(stock_stats[6]), high52=str(stock_stats[7]))
        try:
            db.session.add(new_search)
            db.session.commit()
            return redirect("/analysis")
        except:
            return "Error searching stock"
    else:
        current = Stock.query.order_by(Stock.id.desc()).first()
        return render_template("analysis.html", current=current)

@app.route("/project")
def project():
    return render_template("project.html")

@app.route("/delete/<int:id>")
def delete(id):
    stock_to_delete = Portfolio.query.get_or_404(id)
    try:
        db.session.delete(stock_to_delete)
        db.session.commit()
        return redirect("/")
    except:
        return "Error deleting stock"

@app.route("/update/<int:id>", methods=["POST", "GET"])
def update(id):
    stock = Portfolio.query.get_or_404(id)
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

@app.route("/pieBreakdown.png")
def pieBreakdown():
    plt.clf()
    pieChartArray = [num[0] for num in Portfolio.query.with_entities(Portfolio.curTotal).all()]
    pieChartTickers = [num[0] for num in Portfolio.query.with_entities(Portfolio.ticker).all()]
    pieChartExplode = [0.1 for _ in pieChartArray]
    fig, ax = plt.subplots()
    ax.pie(pieChartArray, labels=pieChartTickers, autopct="%.2f%%", pctdistance=0.8, explode=pieChartExplode)
    return nocache(fig_response())

@app.route("/barBreakdown.png")
def barBreakdown():
    plt.clf()
    labels = [str(name[0]) for name in Portfolio.query.with_entities(Portfolio.name).all()]
    values = [float(num[0]) for num in Portfolio.query.with_entities(Portfolio.pl).all()]
    #values = [float(num[0]) for num in Portfolio.query.with_entities(Portfolio.curTotal).all()]
    fig, ax = plt.subplots()
    ax.bar(labels, values)
    return nocache(fig_response())

def fig_response():
    img = BytesIO()
    plt.savefig('./static/images/img')
    img.seek(0)
    return send_file(img, mimetype='image/png')

def nocache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
