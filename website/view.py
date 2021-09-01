from flask import Blueprint, render_template, request
from .model import *
from datetime import datetime
from . import db
from .analysis_tools.sql_queries import SqlQuery
from .analysis_tools.data_queries import QueryPortfolio
from .analysis_tools.market_data_queries import MarketQuery
from . import styling

view = Blueprint('views', __name__)

headings = (
    "Stock",
    "Av. Buy Price",
    "Target Price",
    "Current Price",
    "% of Portfolio",
    "No. Shares",
    "Buy value",
    "Target value",
    "Current value",
    "Target Gain",
    "Current Gain",
    "Pound value",
)

data = (
    ("S&P 500, Vanguard Idx Fund", 58, 62, 58, 10, 3, 173, 186, 173, 12, 1, 159),
    ("Mcaffee", 58, 62, 58, 10, 3, 173, 186, 173, 12, 1, 159),
    ("Mcaffee", 58, 62, 58, 10, 3, 173, 186, 173, 12, 1, 159),
)

sqlQuery = SqlQuery()
portfolio = QueryPortfolio()


# wrapper method, providing data with colours
def colourful_data(main_data, **kwargs):
    return {'stocks': styling.coloured_data(data=main_data, **kwargs)}


def render(*args, **kwargs):
    return render_template(*args, route=args[0].split('.')[0], **kwargs)


@view.route('/')
def home():
    start_date, end_date = '2021-07-20', '2021-09-01'
    df = portfolio.get_adjusted_price_change(start_date, end_date)

    timescale = [day.strftime('%d %b %Y') for day in df.index.to_list()[1:]]
    portfolio_price_change = ['{:.2f}'.format(value) for value in df['sum'].to_list()[1:]]
    portfolio_price_changes = ['{:.2f}'.format(value) for value in df.values[-1].tolist()]
    portfolio_performance = portfolio.get_trade_performance(start_date, end_date)['perc_change'].tolist()

    sp500 = MarketQuery('^GSPC')
    sp500_price = sp500.get_price_perc_change_aslist(start_date, end_date)

    return render(
        "home.html",
        portfolio_value=sqlQuery.get_portfolio_value(), num_investments=sqlQuery.get_num_investments(),
        headings=headings, data=data,
        timescale=timescale,
        portfolio_price=portfolio_price_change, sp500_price=sp500_price, portfolio_prices=portfolio_price_changes, portfolio_performance=portfolio_performance,
        **colourful_data(
            main_data=sqlQuery.get_tickers(),                # tickers with colours associated to them
            percentages=sqlQuery.get_ticker_distribution(),  # percentage of portfolio for each ticker
        )
    )


@view.route('/trades', methods=["POST", "GET"])
def trades():
    if request.method == "POST":
        # Log new trade in database
        order = 0 if "buy" in request.form else 1
        new_trade = Trade(
            order=order,
            ticker=request.form['ticker'].upper(),
            price=request.form['price'],
            date=datetime.strptime(request.form['date'], '%Y-%m-%dT%H:%M'),
        )
        db.session.add(new_trade)
        db.session.commit()

    return render("trades.html", trade_data=Trade.query.order_by(Trade.date.asc()).all())
