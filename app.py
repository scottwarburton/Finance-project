from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import matplotlib as mpl
mpl.use('agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib import cm
import matplotlib.transforms as transforms
import numpy as np
from matplotlib.patches import Circle, Wedge, Rectangle
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
    daily_return = db.Column(db.String(20))
    beta = db.Column(db.Numeric(9, 2))
    mcap = db.Column(db.String(10))
    pe = db.Column(db.Numeric(9, 2))
    low52 = db.Column(db.Numeric(9, 2))
    high52 = db.Column(db.Numeric(9, 2))
    def __repr__(self):
        return "<Stock %r>" % self.id

class Market(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10))
    name = db.Column(db.String(20))
    price = db.Column(db.Numeric(9, 2))
    daily_return = db.Column(db.String(20))
    def __repr__(self):
        return "<Market %r>" % self.id

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
        stock_daily_return = soup.find("div", {"class": "D(ib) Va(m) Maw(65%) Ov(h)"}).find("div").find_all("span")[
            1].text
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

def market_index_update(index):
    url = "https://finance.yahoo.com/quote/" + str(index.ticker)
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "lxml")
    index.price = float(soup.find("span", {"class": "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text.replace(",",""))
    index.daily_return = soup.find("div", {"class": "D(ib) Va(m) Maw(65%) Ov(h)"}).find("div").find_all("span")[1].text

def market_index_setup(index):
    url = "https://finance.yahoo.com/quote/" + str(index)
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "lxml")
    index_name = soup.find("div", {"class": "D(ib) Mt(-5px) Mend(20px) Maw(56%)--tab768 Maw(52%) Ov(h) smartphone_Maw(85%) smartphone_Mend(0px)"}).find_all("div")[0].find("h1").text
    index_price = float(soup.find("span", {"class": "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text.replace(",",""))
    index_return = soup.find("span", {"class": "Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px)"})
    return Market(ticker=index, name=index_name, price=index_price, daily_return=index_return)

@app.route("/", methods=["POST", "GET"])
def dashboard():
    if (request.method == "POST") and (request.form["submit"] == "Add To Portfolio"):
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
    elif (request.method == "POST") and (request.form["submit"] == "Refresh Prices"):
        updatePL()
        return redirect("/")
    else:
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

@app.route("/market", methods=["POST", "GET"])
def market():
    if len(Market.query.all()) == 0:
        indices_list = ["^SPX", "^IXIC", "^FTSE", "^N225", "^HSI", "^AXJO"]
        for index in indices_list:
            try:
                db.session.add(market_index_setup(index))
                db.session.commit()
            except:
                return "Error adding index"
        return redirect("/market")
    elif request.method == "POST":
        indices = Market.query.all()
        for index in indices:
            market_index_update(index)
            try:
                db.session.commit()
            except:
                return "Error updating indices"
        return redirect("/market")
    else:
        indices = Market.query.order_by(Market.id).all()
        return render_template("market.html", indices=indices)

@app.route("/delete/<int:id>")
def delete(id):
    stock_to_delete = Portfolio.query.get_or_404(id)
    try:
        db.session.delete(stock_to_delete)
        db.session.commit()
        return redirect("/")
    except:
        return "Error deleting stock"

@app.route("/pieBreakdown.png")
def pieBreakdown():
    plt.clf()
    pieChartArray = [num[0] for num in Portfolio.query.with_entities(Portfolio.curTotal).all()]
    pieChartTickers = [num[0] for num in Portfolio.query.with_entities(Portfolio.ticker).all()]
    pieChartExplode = [0.1 for _ in pieChartArray]
    fig, ax = plt.subplots()
    ax.pie(pieChartArray, labels=pieChartTickers, autopct="%.2f%%", pctdistance=0.8, explode=pieChartExplode)
    ax.set_xlabel("Portfolio Breakdown", fontdict={'fontname': 'serif', 'fontsize': 18, 'fontweight': 'bold'})
    plt.style.use("ggplot")
    fig.tight_layout()
    return nocache(fig_response(fig))

@app.route("/barBreakdown.png")
def barBreakdown():
    plt.clf()
    labels = [str(name[0]) for name in Portfolio.query.with_entities(Portfolio.ticker).all()]
    values = [float(num[0]) for num in Portfolio.query.with_entities(Portfolio.pl).all()]
    #values = [float(num[0]) for num in Portfolio.query.with_entities(Portfolio.curTotal).all()]
    fig, ax = plt.subplots()
    ax.bar(labels, values, color="blue")
    ax.set_xlabel("Profit/Loss Breakdown", fontdict={'fontname': 'serif', 'fontsize': 18, 'fontweight': 'bold'})
    ax.set_xticklabels(labels, rotation=45)
    fig.tight_layout()
    return nocache(fig_response(fig))

@app.route("/gaugePE.png")
def gaugePE():
    plt.clf()
    pe_level = Stock.query.order_by(Stock.id.desc()).first().pe
    arrow_num = gauge_pe_arrow(pe_level)
    labels = ['< 0', '0-5x', '5-10x', '10-15x', '15-20x', '20-25x', '> 25x']
    fig = gauge(arrow_num, labels, 'P/E Gauge')
    return nocache(fig_response(fig))

@app.route("/gaugeBeta.png")
def gaugeBeta():
    plt.clf()
    beta_level = Stock.query.order_by(Stock.id.desc()).first().beta
    arrow_num = gauge_beta_arrow(beta_level)
    labels = ['< -1', '-1-0x', '0-1x', '> 1x']
    fig = gauge(arrow_num, labels, 'Beta Gauge')
    return nocache(fig_response(fig))

@app.route("/highlow52.png")
def highlow52():
    plt.clf()
    fig = plt.figure(figsize=(8, 3))
    ax = fig.add_axes([0, 0, 0.9, 0.15])
    low = float(Stock.query.order_by(Stock.id.desc()).first().low52)
    high = float(Stock.query.order_by(Stock.id.desc()).first().high52)
    price = float(Stock.query.order_by(Stock.id.desc()).first().price)
    cmap = mpl.cm.seismic
    norm = mpl.colors.Normalize(vmin=low, vmax=high)
    cb = mpl.colorbar.ColorbarBase(ax, cmap=cmap, norm=norm, orientation='horizontal')
    bbox_props = dict(boxstyle="rarrow,pad=0.3", fc="blue", lw=2)
    ax.text(-0.085, 2.45, "Lowest Price", ha="center", va="center", color="w", rotation=315, size=15,
            transform=ax.transAxes, bbox=bbox_props)
    bbox_props = dict(boxstyle="larrow,pad=0.3", fc="red", lw=2)
    ax.text(1.09, 2.45, "Highest Price", ha="center", va="center", color="w", rotation=45, size=15,
            transform=ax.transAxes, bbox=bbox_props)
    bbox_props = dict(boxstyle="larrow,pad=0.3", fc="green", lw=2)
    trans = transforms.blended_transform_factory(ax.transData, ax.transAxes)
    ax.text(price, 2.25, "Current Price", ha="center", va="center", color="w", rotation=90, size=15,
            transform=trans, bbox=bbox_props)
    cb.set_label('52wk Price Range', fontdict={'fontname': 'serif', 'fontsize': 18, 'fontweight': 'bold'})
    return nocache(fig_response(fig))

def fig_response(fig):
    img = BytesIO()
    fig.savefig(img, bbox_inches="tight")
    img.seek(0)
    plt.close(fig)
    return send_file(img, mimetype='image/png')

def nocache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

def gauge_pe_arrow(pe_level):
    pe_levels = [0, 5, 10, 15, 20, 25]
    for level in pe_levels:
        if pe_level < level:
            return pe_levels.index(level) + 1
    return 7

def gauge_beta_arrow(beta_level):
    beta_levels = [-1, 0, 1]
    for level in beta_levels:
        if beta_level < level:
            return beta_levels.index(level) + 1
    return 4

def degree_range(n):
    start = np.linspace(0, 180, n + 1, endpoint=True)[0:-1]
    end = np.linspace(0, 180, n + 1, endpoint=True)[1::]
    mid_points = start + ((end - start) / 2.)
    return np.c_[start, end], mid_points

def rot_text(ang):
    rotation = np.degrees(np.radians(ang) * np.pi / np.pi - np.radians(90))
    return rotation

def gauge(arrow, labels, title):
    colors = 'seismic_r'
    N = len(labels)
    if isinstance(colors, str):
        cmap = cm.get_cmap(colors, N)
        cmap = cmap(np.arange(N))
        colors = cmap[::-1, :].tolist()
    if isinstance(colors, list):
        if len(colors) == N:
            colors = colors[::-1]
        else:
            raise Exception("\n\nnumber of colors {} not equal \
            to number of categories{}\n".format(len(colors), N))
    fig, ax = plt.subplots()
    ang_range, mid_points = degree_range(N)
    labels = labels[::-1]
    patches = []
    for ang, c in zip(ang_range, colors):
        patches.append(Wedge((0., 0.), .4, *ang, facecolor='w', lw=2))
        patches.append(Wedge((0., 0.), .4, *ang, width=0.10, facecolor=c, lw=2, alpha=0.5))
    [ax.add_patch(p) for p in patches]
    for mid, lab in zip(mid_points, labels):
        ax.text(0.35 * np.cos(np.radians(mid)), 0.35 * np.sin(np.radians(mid)), lab, \
                horizontalalignment='center', verticalalignment='center', fontsize=14, \
                fontweight='bold', fontname='serif', rotation=rot_text(mid))
    r = Rectangle((-0.4, -0.1), 0.8, 0.1, facecolor='w', lw=2)
    ax.add_patch(r)
    ax.text(0, -0.05, title, horizontalalignment='center', \
            verticalalignment='center', fontsize=18, fontweight='bold', fontname='serif')
    pos = mid_points[abs(arrow - N)]
    ax.arrow(0, 0, 0.225 * np.cos(np.radians(pos)), 0.225 * np.sin(np.radians(pos)), \
             width=0.04, head_width=0.09, head_length=0.1, fc='k', ec='k')
    ax.add_patch(Circle((0, 0), radius=0.02, facecolor='k'))
    ax.add_patch(Circle((0, 0), radius=0.01, facecolor='w', zorder=11))
    ax.set_frame_on(False)
    ax.axes.set_xticks([])
    ax.axes.set_yticks([])
    ax.axis('equal')
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
