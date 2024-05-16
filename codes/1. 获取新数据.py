# 根据索引获取缺失的数据
import pandas as pd
from datetime import datetime, timedelta
import jqdatasdk as jq
import os


jq.auth('17614781955', '1598647asdD')
stock_list = pd.read_csv('../stock_data/stock_list.csv', parse_dates=['start_date', 'end_date'], index_col='code')


def get_industries_component():
    """ 获取行业成分股列表 """
    industry_list = pd.read_csv('../stock_data/industries_list.csv', index_col='code')
    for index, row in industry_list.iterrows():
        name = row['name']
        df = {name: jq.get_industry_stocks(index, date=None)}
        df = pd.DataFrame(df)
        df.to_csv(f'../stock_data/industry/{index}_{name}.csv')
    print('已获取行业成分股列表')


def get_concepts_data_component():
    """ 获取概念成分股列表 """
    concepts_list = pd.read_csv('../stock_data/concepts_list.csv', index_col='code')
    for index, row in concepts_list.iterrows():
        name = row['name']
        df = {name: jq.get_concept_stocks(index, date=None)}
        df = pd.DataFrame(df)
        df.to_csv(f'../stock_data/concepts/{index}_{name}.csv')
    print('已获取概念成分股列表')


def get_industries_data():
    """ 获取行业列表 """
    print('已获取行业列表')
    df = jq.get_industries()
    df.index_col = 0
    df.index.name = 'code'
    df.to_csv('../stock_data/industries_list.csv')


def get_concepts_data():
    """ 获取概念列表 """
    print('已获取概念列表')
    df = jq.get_concepts()
    df.index_col = 0
    df.index.name = 'code'
    df.to_csv('../stock_data/concepts_list.csv')


def get_stock_list():
    """获取所有股票列表"""
    global stock_list

    df = jq.get_all_securities()
    df.index.name = 'code'
    new_row = {
        'start_date': pd.to_datetime('2005-01-01'),
        'end_date': pd.to_datetime('2022-01-01'),
    }
    new_df = pd.DataFrame(new_row, index=['000001.XSHG', '000300.XSHG'])
    df = pd.concat([new_df, df], ignore_index=False)
    df.index.name = 'code'
    df.to_csv('../stock_data/stock_list.csv')
    print('已更新stock_list')


def get_history_daily_data():
    """补充日线的历史数据， 更新到stock_data/daily_data目录中"""
    for start_date, code in zip(stock_list['start_date'], stock_list.index):
        print(f"正在获取{code}历史数据", end='   ')
        try:
            df = pd.read_csv(f'../stock_data/daily_data/{code}.csv', index_col=0, parse_dates=True)
            if df.shape[0] == 0:
                end_date = datetime.now()
            else:
                end_date = df.iloc[0].name - timedelta(days=1)  # 前一天
            new_data = jq.get_price(code, start_date=start_date, end_date=end_date, frequency='1d')
            print(f'使用流量{len(new_data)}行')
            update_data = pd.concat([new_data, df])
            update_data = update_data.drop_duplicates(keep='first')  # 去重
            update_data.to_csv(f'../stock_data/daily_data/{code}.csv')
        except (FileNotFoundError, pd.errors.EmptyDataError):
            end_date = datetime.now()
            df = jq.get_price(code, start_date=start_date, end_date=end_date, frequency='1d')
            print(f'新股票：使用流量{len(df)}行')
            df.to_csv(f'../stock_data/daily_data/{code}.csv')


def get_new_daily_data():
    """获取新的日线数据，更新到stock_data/daily_data目录中"""
    for code, row in stock_list.iterrows():
        try:
            print(f"正在更新{code}", end='  ')
            df = pd.read_csv(f'../stock_data/daily_data/{code}.csv', index_col=0, parse_dates=True)

            if df.shape[0] == 0 or row['end_date'] < datetime.today():
                if df.shape[0] == 0:
                    print('没有数据')
                else:
                    print('退市了')
                continue
            start_date = (df.iloc[-1].name + timedelta(days=1)).strftime("%Y-%m-%d")  # 后一天
            end_date = datetime.today().strftime("%Y-%m-%d")
            new_data = jq.get_price(code, start_date=start_date, end_date=end_date, frequency='1d')
            print(f'使用流量{len(new_data)}行')
            update_data = pd.concat([df, new_data])
            update_data = update_data.drop_duplicates(keep='first')  # 去重
            update_data.to_csv(f'../stock_data/daily_data/{code}.csv')
        except FileNotFoundError:
            print('没有数据,正在获取')
            new_data = jq.get_price(code, start_date='2010-01-01', end_date=datetime.today(), frequency='1d')
            print(f'使用流量{len(new_data)}行')
            new_data.to_csv(f'../stock_data/daily_data/{code}.csv')


def get_history_minute_data():
    """补充历史分时数据，跟新到stock_data/minute_data目录中"""
    for start_date, code in zip(stock_list['start_date'], stock_list.index):
        # 使用os.path.exists()检查文件是否存在,存在返回 True
        if not os.path.exists(f'../stock_data/minute_data/{code}_m.csv'):
            print(f"正在获取{code}的历史分时数据")
            end_date = datetime.now()
            data = jq.get_price(code, start_date=start_date, end_date=end_date, frequency='1m')
            data.to_csv(f'../stock_data/minute_data/{code}_m.csv')
        else:
            print(f'{code}的分时历史数据已存在，无需获取')


def get_money_flow():
    """获取资金流数据，存放在../stock_data/money_flow目录中"""
    for stock_code, row in stock_list.iterrows():
        if stock_code == '000001.XSHG' or stock_code == '000300.XSHG':
            continue
        print(f"正在获取{stock_code}的资金流数据")
        df = jq.get_money_flow(stock_code, row['start_date'], row['end_date'])
        df.set_index('date', inplace=True)
        df.to_csv(f'../stock_data/money_flow/{stock_code}.csv')


def get_all_trade_days():
    df = pd.DataFrame(jq.get_all_trade_days(), columns=['date'])
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['date'] <= datetime.now()]
    df.to_csv(f'../stock_data/date_list.csv')


def main():
    # 重新获取数据
    # df = jq.get_price('000056.XSHE', start_date='1998-01-01', end_date=datetime.today(), frequency='1d')
    # print(df)
    # df.to_csv(rf'../stock_data/daily_data/000056.XSHE.csv')
    # exit()

    if datetime.now().day % 7 == 2:
        get_concepts_data()  # 概念
        get_industries_data()  # 行业
        get_industries_component()  # 行业成分股
        get_concepts_data_component()  # 概念成分股
        get_stock_list()  # 所有股票列表

    get_history_daily_data()
    get_all_trade_days()
    get_money_flow()  # 获取资金流数据，浪费数据，待改进
    #
    get_new_daily_data()
    get_history_minute_data()

    # 获取新的分时数据（还没写）
    # get_new_minute_data()


if __name__ == '__main__':
    start_time = datetime.now()  # 用来计时
    main()
    print(datetime.now() - start_time)
