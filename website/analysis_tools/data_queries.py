from .market_data_queries import MarketQuery
from .sql_queries import SqlQuery
import pandas as pd


class QueryPortfolio(object):
    """
    Combines the portfolio dataset (acquired by SqlQuery), and
    """

    def __init__(self, index_ticker='^GSPC'):
        self.index = MarketQuery(index_ticker)
        self.sql_query = SqlQuery()

    def get_price_perc_change(self, start, end):
        """
        Used for theoretical portfolio performance (if all current stocks were bought at the same start period)

        :param start: YYYY-MM-DD
        :param end: YYYY-MM-DD
        :return: numpy object
        """

        # track performance of each ticker
        # superimpose into portfolio performance (theoretical)
        tickers_change = pd.DataFrame()
        for ticker in self.sql_query.get_tickers():
            ticker_obj = MarketQuery(ticker)
            ticker_change = ticker_obj.get_price_perc_change(start=start, end=end)

            tickers_change[ticker] = ticker_change['% change']

        # Date         MSFT   DARK  ...  sum
        # 2021-07-26   -1.9   -2.0  ... -3.9
        # ...
        tickers_change['sum'] = tickers_change.sum(axis=1)

        return tickers_change

    def get_adjusted_price_change(self, start, end):
        """
        Adjust daily percentage price change by accounting for portion of portfolio
        each stock represents.
        Currently, done simply by multiplying each stock % change by the % of portfolio it is

        :param start: YYYY-MM-DD
        :param end: YYYY-MM-DD
        :return: numpy object
        """

        portfolio_change = self.get_price_perc_change(start, end)

        adjusted_portfolio = pd.DataFrame()

        for i, ticker in enumerate(self.sql_query.get_tickers()):
            percentage = self.sql_query.get_ticker_distribution()[i]
            adjusted_portfolio[ticker] = portfolio_change[ticker] * (percentage/100)

        # recalculate sum
        adjusted_portfolio['sum'] = adjusted_portfolio.sum(axis=1)

        print("\nCumulative % change:")
        print(adjusted_portfolio)
        return adjusted_portfolio

    def get_trade_prices(self, start, end):
        """
        Get the prices of stocks in portfolio, indexed by date
        :param start: YYYY-MM-DD
        :param end: YYYY-MM-DD
        :return:
        """
        trades = self.sql_query.get_all_trades()
        combined_trade_data = pd.DataFrame(index=pd.bdate_range(start=start, end=end))

        # track performance of each trade
        # superimpose into portfolio performance
        for trade in trades:
            trade_query = MarketQuery(trade.ticker)
            trade_data = trade_query.get_price_by_date(trade.date, end)
            # rename column to trade ticker
            trade_data = trade_data.rename(columns={'Close': trade.ticker})

            # if ticker already exists
            if trade.ticker in combined_trade_data:
                combined_trade_data[trade.ticker] = combined_trade_data[trade.ticker].add(trade_data[trade.ticker], fill_value=0)
            else:
                # superimpose into overall portfolio performance
                combined_trade_data = combined_trade_data.join(trade_data)

        # replace NaN values with first occurring price
        # assumes NaN values only occur at the starting rows
        #  -> under the assumption that stocks can be bought at any time, but are held until end period
        combined_trade_data = combined_trade_data.fillna(method="bfill")

        return combined_trade_data

    def get_trade_performance(self, start, end):
        """
        Used for actual portfolio performance.
        Get the performance of each individual trade, and superimpose each them

        :return:
        """
        trade_data = self.get_trade_prices(start, end)

        # get change in price
        trade_change_data = trade_data.diff()
        # get price change sum for each day
        trade_change_data = trade_change_data.sum(axis=1)
        # actual price sum (of day before)
        trade_sum_data = trade_data.sum(axis=1).shift(1)

        trade_data['perc_change'] = 100 * (trade_change_data / trade_sum_data).cumsum()

        trade_data = trade_data.fillna(0)
        print("\nTrade performance:")
        print(trade_data)

        return trade_data

