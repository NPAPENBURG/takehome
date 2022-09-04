import sqlite3
import yfinance
import csv
import argparse
from datetime import datetime, timedelta
import sys


def query_stocks():
    """This function is used to connect/query the SQLite database to grab data"""

    con = sqlite3.connect("stock_portfolio.sqlite")
    cur = con.cursor()

    query = """SELECT S.symbol, SUM(quantity)
                FROM portfolio P
                JOIN stocks S
                ON S.id = P.stock_id
                GROUP BY P.stock_id
                ORDER BY P.stock_id"""

    res = cur.execute(query)
    res = res.fetchall()
    return [list(stock) for stock in res]


def is_date():
    """This function is to pass a date in as a command line parameter and check to make sure it is a date"""

    parser = argparse.ArgumentParser()
    parser.add_argument('--date', dest='date', type=str, help='Query By Date')
    args = parser.parse_args()
    date = args.date

    try:
        start_date = datetime.strptime(date, '%Y-%m-%d').date()
        end_date = start_date + timedelta(days=1)
        return start_date, end_date

    except ValueError:
        print("Please use the following date format: 2022-01-01")
        sys.exit(1)


def create_csv(stocks_list):
    """This is our main function that is going to grab the additional information from yFiance so we can create the csv
    file with the data requested for this project"""

    for stock in stocks_list:
        dates = is_date()
        try:
            close_price = yfinance.Ticker(stock[0]).history(start=dates[0], end=dates[1]).Close[0].round(2)
            total_value = (close_price * stock[1]).round(2)
            stock.insert(0, is_date()[0])
            stock.append(close_price)
            stock.append(total_value)

        except IndexError:
            print("or the market was closed on this day.")

    with open('stocks.csv', 'w', newline='') as out:
        csv_out = csv.writer(out)
        csv_out.writerow(['date', 'stock_symbol', 'total_quantity', 'close_price', 'total_value'])
        for stock in stocks_list:
            csv_out.writerow(stock)


if __name__ == "__main__":
    stocks = query_stocks()
    create_csv(stocks)
