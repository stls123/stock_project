import pandas as pd
import jqdatasdk as jq
jq.auth('17614781955', '1598647asdD')
stock_list = pd.read_csv('../stock_data/stock_list.csv', index_col=0, parse_dates=True)


def remove_duplicates():
    """
    去重
    """
    # 读取CSV文件
    for start_date, code in zip(stock_list['start_date'], stock_list['code']):
        print(f"开始去除{code}的重复行")
        df = pd.read_csv(f'stock_data/daily_data/{code}.csv', index_col=0, parse_dates=True)
        # 查找重复行（标记：除了重复行的第一行 之外的所有重复行）
        duplicates = df.duplicated(keep='first')
        # print(df[duplicates])
        # 去重（保留重复行的第一行）
        df = df[~duplicates]
        df.to_csv(f'stock_data/daily_data/{code}.csv')

        # 下面两行可以打印数据被处理后重复的行数
        # duplicates = df.duplicated(keep=False)  # keep=False表示找出所有重复项，而不仅仅是第一次出现的
        # print(len(df[duplicates]))


def get_money_flow():
    for stock_code, row in stock_list.iterrows():
        if stock_code == '000001.XSHG' or stock_code == '000300.XSHG':
            continue
        df = jq.get_money_flow(stock_code, row['start_date'], row['end_date'])
        df.set_index('date', inplace=True)
        df.to_csv(f'../stock_data/money_flow/{stock_code}.csv')


# remove_duplicates()
get_money_flow()

