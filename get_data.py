import os
from datetime import datetime, timedelta, date
import logging
import pandas as pd
import argparse

import yfinance as yf
from configure import config

stock_wikiinfo_path = "dataset/stock_wikiinfo_path.csv"

# get spstock names from wikipedia
def get_sp500_stocks() -> pd.DataFrame:
    table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    logging.info(f"All {len(table)} stocks")
    return table

def download_stock_data_start_end(where, start_date, end_date):
    if where == "hsi":
        stocks_df = pd.read_csv("dataset/恒生指数成分股.csv", index_col=False)
        stocks_name = [f"{x:04d}"+".HK" for x in stocks_df["代码"].to_list()]
    elif where == "sp500":
        stocks_df = pd.read_csv("dataset/stock_wikiinfo_path.csv", index_col=False)
        stocks_name = stocks_df["Symbol"].to_list()
    df = yf.download(tickers=stocks_name, start=start_date, end=end_date, interval="1d")
    start_date_yyyymmdd = datetime.strftime(datetime.strptime(start_date, "%Y-%m-%d"), "%Y%m%d")
    end_date_yyyymmdd = datetime.strftime(datetime.strptime(end_date, "%Y-%m-%d"), "%Y%m%d")
    df.to_parquet(f"dataset/{where}_{start_date_yyyymmdd}_{end_date_yyyymmdd}.parquet")

# get stock data of a specific stock of last year
def download_stock_data(stock_name_list, days=1, partition_cols=["Date"], save_path=None) -> pd.DataFrame:
    today = date.today()
    start = today - timedelta(days=days)
    print("start = ", start)
    data : pd.DataFrame = yf.download(" ".join(stock_name_list), start = start, end=today)
    data.index = data.index.strftime("%Y-%m-%d")
    data.to_parquet(save_path, engine="pyarrow", compression="gzip", partition_cols=partition_cols)
    return data


def download_stock_by_ticker(ticker_list, start_date, end_date) -> pd.DataFrame:
    for ticker in ticker_list:
        data = yf.download(ticker, start=start_date, end=end_date, interval="1d")
        data.index = data.index.strftime("%Y-%m-%d")
        data.to_parquet(f"{stock_datapath}/{ticker}.parquet", engine="pyarrow", compression="gzip")


def transform(df):
    df = df.T
    df.reset_index(inplace=True)
    df.columns = ["Ticker", "Price", "value"]
    df = df.pivot(index="Ticker", columns="Price", values=df.columns[2:])
    df.columns = df.columns.droplevel(0)
    return df

def get_oneday_stock_data(stock_name_list, stock_datapath, target_date):
    if not os.path.exists(f"{stock_datapath}/Date={target_date}"):
        data = yf.download(
            " ".join(stock_name_list), 
            start=target_date, 
            end=(datetime.strptime(target_date, "%Y-%m-%d")+timedelta(days=1)).strftime("%Y-%m-%d"), 
            group_by="ticker", threads=1)
        data.index = data.index.strftime("%Y-%m-%d")
        data.to_parquet(stock_datapath, engine="pyarrow", compression="gzip", partition_cols=["Date"])
        print(f"{target_date} stock is downloaded to {stock_datapath}")
    else:
        print(f"{stock_datapath}/Date={target_date} already exists")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, default="2025-08-09")
    parser.add_argument("--start_date", type=str)
    parser.add_argument("--end_date", type=str)
    parser.add_argument("--where", default="hk", type=str)
    args = parser.parse_args()
    if args.where == "us":
        if os.path.exists(stock_wikiinfo_path):
            stock_wikiinfo = pd.read_csv(stock_wikiinfo_path)
        else:
            stock_wikiinfo = get_sp500_stocks()
            stock_wikiinfo.to_csv(stock_wikiinfo_path)
        stock_name_list = stock_wikiinfo["Symbol"].to_list()
        stock_datapath = config.stock_datapath
    elif args.where == "hk":
        hsi_stocks_df = pd.read_csv("data/恒生指数成分股.csv")
        stock_name_list = [f"{x:04d}"+".HK" for x in hsi_stocks_df["代码"].to_list()]
        stock_datapath = config.hsi_datapath

    if args.start_date is not None:
        current_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            get_oneday_stock_data(stock_name_list, stock_datapath, date_str)
            current_date += timedelta(days=1)
    else:
        get_oneday_stock_data(stock_name_list, stock_datapath, args.date)
    # download_stock_data(stock_name_list, days=100, partition_cols=["Date"], save_path=stock_datapath)