import yfinance as yf


class MarketQuery(object):
    """
    Query real market data from Yahoo finance
    """

    def __init__(self, ticker):
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)

    def get_financials(self):
        return self.stock.financials

    def get_price_by_date(self, start, end):
        """
        Get the stock price between particular dates

        :param start: YYYY-MM-DD
        :param end: YYYY-MM-DD
        :return: numpy object
        """
        return self.stock.history(start=start, end=end).filter(['Close'])

    def get_price_perc_change(self, start, end):
        """
        Calculate % change between stock prices every day. Take cumulative sum to find % change from start to end period

        :param start: YYYY-MM-DD
        :param end: YYYY-MM-DD
        :return: dataframe containing cumulative % change in price between start to end period, interval of single day
        """
        price = self.get_price_by_date(start, end)
        price['change'] = price['Close'].diff()
        price['% change'] = 100 * (price.change / price.Close)

        return price.cumsum()

    def get_price_perc_change_aslist(self, start, end):
        """
        Get the cumulative change in price every day

        :param start: YYYY-MM-DD
        :param end: YYYY-MM-DD
        :return: cumulative % change in price between start to end period, interval of single day
        """
        return self.get_price_perc_change(start, end)['% change'].to_list()[1:]
