from website import db
from website.model import Trade
from sqlalchemy.sql import func


class SqlQuery(object):
    """
    Query investment data from our own database
    """

    def get_tickers(self):
        """
        Query distinct tickers.

        :returns List of strings, ticker symbols
        """
        return [val[0] for val in db.session.query(Trade.ticker).distinct()]

    def get_num_investments(self):
        return len(self.get_tickers())

    def get_portfolio_value(self):
        """
        Query total portfolio value. Account for 'sell', portfolio value = buy - sell

        :returns Float, portfolio value
        """
        # SELECT SUM(price) AS "sumPortfolio"
        # FROM trade
        # WHERE order=0;

        buy_value = Trade.query.with_entities(
            func.sum(Trade.price).label("sumPortfolio")
        ).filter(
            Trade.order == 0
        ).first().sumPortfolio

        buy_value = 0 if buy_value is None else buy_value

        sell_value = Trade.query.with_entities(
            func.sum(Trade.price).label("sumPortfolio")
        ).filter(
            Trade.order == 1
        ).first().sumPortfolio

        sell_value = 0 if sell_value is None else sell_value

        return buy_value - sell_value

    def get_ticker_distribution(self):
        """
        ...
        :return: list of floats, % of total portfolio each ticker is
        """
        tickers = self.get_tickers()
        portfolio_sum = self.get_portfolio_value()

        # get total value (price) of each ticker
        totals = []  # assumes order stays the same
        for ticker in tickers:

            # SELECT SUM(price) AS "sumPrice"
            # FROM trade
            # WHERE ticker="DARK";
            # WHERE order=0;
            price_sum = Trade.query.with_entities(
                func.sum(Trade.price).label("sumPrice")
            ).filter(
                Trade.ticker == ticker
            ).filter(
                Trade.order == 0
            ).first()

            # get total price from specified column
            sumPrice = price_sum.sumPrice

            if sumPrice is not None:
                # calculate the % of portfolio this is, add to list
                totals.append(round(100 * sumPrice/portfolio_sum, 2))
            else:
                totals.append(0)

        return totals

    def get_all_trades(self, order=0):
        """
        Get all the trade data from the database

        :param order: The date order in which to return the data. 0 - ascending, 1 - descending
        :return: SQL obj of trade data
        """
        if order:
            return Trade.query.order_by(Trade.date.desc()).all()
        else:
            return Trade.query.order_by(Trade.date.asc()).all()

