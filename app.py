

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskdb.db'
db = SQLAlchemy(app)

class Stocks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False)
    units = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return "<Stock %r>" % self.id

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        new_stock = Stocks(ticker=request.form["ticker"], units=request.form["units"], price=request.form["price"])
        try:
            db.session.add(new_stock)
            db.session.commit()
            return redirect("/")
        except:
            return "Error adding stock"
    else:
        stocks = Stocks.query.order_by(Stocks.date_added).all()
        return render_template("index.html", stocks=stocks)

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
        stock.ticker = request.form["ticker"]
        stock.units = request.form["units"]
        try:
            db.session.commit()
            return redirect("/")
        except:
            return "Error updating stock"
    else:
        return render_template("index.html", stock=stock)


if __name__ == "__main__":
    app.run(debug=True)






