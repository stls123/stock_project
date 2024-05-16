import jqdatasdk as jq

import pandas as pd

pd.set_option('display.max_columns', 1000)
# pd.set_option('display.max_rows', 1000)

jq.auth('17614781955', '1598647asdD')
stock_list = pd.read_csv('../stock_data/stock_list.csv', parse_dates=['start_date', 'end_date'], index_col='code')


def get_600data():
    date_df = pd.read_csv(f'../stock_data/date_list.csv', index_col=0)
    rising_600_count = {}  # 上涨家数
    falling_600_count = {}  # 下跌家数
    flat_600_count = {}  # 横盘家数
    stock_600_list = stock_list[stock_list.index.str[:3] == '600']

    for date in date_df['date']:
        rising_600_count[str(date)] = 0
        falling_600_count[str(date)] = 0
        flat_600_count[str(date)] = 0

    for stock_code in stock_600_list.index:
        signal_stock_data = pd.read_csv(f'../stock_data/daily_data/{stock_code}.csv', index_col='date')
        signal_stock_data = signal_stock_data[['close']]
        signal_stock_data['zf_shift1'] = signal_stock_data['close'] - signal_stock_data['close'].shift(1)
        for date in date_df['date']:
            try:
                # print(signal_stock_data.loc[date, 'zf_shift1'])
                if signal_stock_data.loc[date, 'zf_shift1'] > 0:
                    rising_600_count[date] += 1
                    print(rising_600_count)
                elif signal_stock_data.loc[date, 'zf_shift1'] < 0:
                    falling_600_count[date] += 1
                else:
                    flat_600_count[date] += 1
                print(stock_code, date)
            except KeyError:
                print(stock_code, date)
                continue


def get_30data():
    pass


get_600data()
