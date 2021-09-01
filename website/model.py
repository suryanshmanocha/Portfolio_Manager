from . import db
from sqlalchemy.sql import func


class Trade(db.Model):

    id = db.Column(db.Integer, primary_key=True)       # UUID of each trade
    order = db.Column(db.Boolean)                      # 0: Buy order, 1: Sell order
    ticker = db.Column(db.String(6))                   # Stock symbol
    price = db.Column(db.Float)                        # Transaction price
    shares = db.Column(db.Float)                       # No. shares - calculated post-input
    date = db.Column(db.DateTime, default=func.now())  # Date of order transaction
