import pandas as pd
from datetime import datetime


def add_daily_ma(df_):
    df_['l_ma3'] = df_['low'].rolling(window=3).mean().round(3)
    df_['l_ma5'] = df_['low'].rolling(window=5).mean().round(3)
    df_['l_ma7'] = df_['low'].rolling(window=7).mean().round(3)
    df_['l_ma9'] = df_['low'].rolling(window=9).mean().round(3)
    df_['l_ma20'] = df_['low'].rolling(window=20).mean().round(3)
    df_['l_ma60'] = df_['low'].rolling(window=60).mean().round(3)
    df_['l_ma120'] = df_['low'].rolling(window=120).mean().round(3)
    df_['l_ma200'] = df_['low'].rolling(window=200).mean().round(3)
    df_['ma3'] = df_['close'].rolling(window=3).mean().round(3)
    df_['ma5'] = df_['close'].rolling(window=5).mean().round(3)
    df_['ma7'] = df_['close'].rolling(window=7).mean().round(3)
    df_['ma9'] = df_['close'].rolling(window=9).mean().round(3)
    df_['ma20'] = df_['close'].rolling(window=20).mean().round(3)
    df_['ma60'] = df_['close'].rolling(window=60).mean().round(3)
    df_['ma120'] = df_['close'].rolling(window=120).mean().round(3)
    df_['ma200'] = df_['close'].rolling(window=200).mean().round(3)

    df_['v_ma3'] = df_['volume'].rolling(window=3).mean().round(3)
    df_['v_ma5'] = df_['volume'].rolling(window=5).mean().round(3)
    df_['v_ma7'] = df_['volume'].rolling(window=7).mean().round(3)
    df_['v_ma9'] = df_['volume'].rolling(window=9).mean().round(3)
    df_['v_ma20'] = df_['volume'].rolling(window=20).mean().round(3)
    df_['v_ma60'] = df_['volume'].rolling(window=60).mean().round(3)
    df_['v_ma120'] = df_['volume'].rolling(window=120).mean().round(3)
    df_['v_ma200'] = df_['volume'].rolling(window=200).mean().round(3)
    df_['zf'] = (abs(df_['close'] - df_['close'].shift(1)) / df_['close'].shift(1)).round(3)
    df_['zf_ma3'] = df_['zf'].rolling(window=3).mean().round(3)
    df_['zf_ma5'] = df_['zf'].rolling(window=5).mean().round(3)
    df_['zf_ma7'] = df_['zf'].rolling(window=7).mean().round(3)
    df_['zf_ma9'] = df_['zf'].rolling(window=9).mean().round(3)
    df_['zf_ma20'] = df_['zf'].rolling(window=20).mean().round(3)
    df_['zf_ma60'] = df_['zf'].rolling(window=60).mean().round(3)
    df_['zf_ma120'] = df_['zf'].rolling(window=120).mean().round(3)
    df_['zf_ma200'] = df_['zf'].rolling(window=200).mean().round(3)
    return df_


# todo 把指数的数据合并到日数据中，还有问题，需要改
def add_index_data(stock_data, stock_code):
    if stock_code == '000001.XSHG' or stock_code == '000300.XSHG':
        return stock_data
    indexdf = pd.read_csv(rf'../stock_data/daily_data/000001.XSHG.csv', index_col=0, parse_dates=True)
    indexdf.index.name = 'date'



    stock_data.index = pd.to_datetime(stock_data.index)
    df_ = pd.merge(stock_data, indexdf, how='left')  # how='left' 表示保留左表（股票数据）的索引
    # df_.set_index('date', inplace=True)  # 设置date列为索引列
    return df_


# 合并数据资金流和股票数据
def merge_data(stock_data, stock_code):
    # print('正在合并资金流数据')
    if stock_code == '000001.XSHG' or stock_code == '000300.XSHG':
        return stock_data
    flow_data = pd.read_csv(fr'../stock_data/money_flow/{stock_code}.csv')
    df_ = pd.merge(stock_data, flow_data, on='date', how='left') # how='left' 表示保留左表（股票数据）的索引
    df_.set_index('date', inplace=True)
    return df_


def main():
    stock_list = pd.read_csv("../stock_data/stock_list.csv")
    # stock_list = stock_list[stock_list['start_date'] <= '2024-01-01']
    for index, row in stock_list.iterrows():
        df = pd.read_csv(f"../stock_data/daily_data/{row['code']}.csv", index_col=0)
        df.index.name = 'date'
        print(row['code'])

        df = df[['open', 'high', 'close', 'low', 'volume', 'money']]  # 格式化数据
        df.drop_duplicates(keep='first', inplace=True)  # 基于索引列删除重复行，keep='first' 表示保留重复行中的第一行,inplace=True表示直接覆盖原有数据，而不创建备份数据
        df = add_daily_ma(df)  # 添加ma列
        df = merge_data(df, row['code'])  # 合并资金流数据到df
        df.drop(['low_date', 'high_date'], axis=1, inplace=True)  # 删除指定列,inplace=True表示直接覆盖原有数据，而不创建备份数据

        # 保存csv文件
        df.to_csv(f"../stock_data/daily_data/{row['code']}.csv", index=True)
        # 保存至  tempfile，用于测试功能
        # df.to_csv(f"../stock_data/tempfile/{row['code']}.csv", index=True)


if __name__ == "__main__":
    t = datetime.now()
    main()
    print(datetime.now() - t)
