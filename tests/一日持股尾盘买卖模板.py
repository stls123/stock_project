import pandas as pd
from colorama import Fore, init  # 字体颜色
import numpy as np
import matplotlib.pyplot as plt
# import multiprocessing as mp  # 多线程
from datetime import datetime
# 设置中文字体，这里以'SimHei'字体为例
plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体为黑体
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号
init()  # 设置字体颜色需要用到


def get_stock_list():
    stock_df = pd.read_csv(r"../stock_data/stock_list.csv", index_col='code',
                           parse_dates=['start_date', 'end_date'])
    stock_df = stock_df[
        (stock_df.index.str[:3] != '688') &
        (stock_df.index.str[0] != '3') &
        (~stock_df['name'].str.contains('ST', na=False)) &
        (stock_df['start_date'] <= pd.to_datetime('2021-01-01')) &
        (stock_df['end_date'] >= pd.to_datetime('2024-01-01'))
        ]
    return stock_df


buy_days = 0  # 买入天数


def buy(df, date):
    global buy_days
    global money, stock_count, old_money, old_stock_money, earnings
    # todo 买入条件
    b0 = stock_count == 0 and df['buy_signal'].loc[date] == 1   # 没有持仓
    if b0 and buy_date_count[date.strftime('%Y-%m-%d')] <= 3:  # 当天最多买8个
        buy_days = 0
        buy_date_count[date.strftime('%Y-%m-%d')] += 1  # 记录当前日期买入一次
        buy_price = df['close'].loc[date]
        old_money = money  # 买入前记录资金状况
        stock_count = (money // (buy_price * 100)) * 100  # 增加股票数量
        money -= stock_count * buy_price  # 减少资金数量
        old_stock_money = stock_count * buy_price  # 买入后存放股票市值
        print(Fore.BLACK + f"{stock_code[:6]}: {str(date)[:10]} 收盘买入:{buy_price}")


def sell(df: pd.DataFrame, date) -> None:
    global money, old_money, stock_count, old_stock_money, earnings, stock_count, buy_days
    if stock_count != 0:
        buy_days += 1  # 持仓天数
    if stock_count != 0 and df['close'].loc[date] > df['open'].loc[date]:  # 卖出条件
        sell_date_count[date.strftime('%Y-%m-%d')] += 1  # 记录当前日期卖出一次
        money += df['close'].loc[date] * stock_count - 20
        earnings.append(round(money - old_money, 2))
        stock_count = 0
        buy_days = 0
        print(Fore.BLACK + f"{stock_code[:6]}: {str(date)[:10]} 收盘卖出:{df['close'].loc[date]}")
        return


def get_buy_signal(stock_code, start_date, end_date):
    """
    num:从哪个位置开始获取前面的数据
    count:获取几个数据（从第i个位置获取数据）
    """
    df = pd.read_csv(fr"../stock_data/daily_data/{stock_code}.csv", index_col=0, parse_dates=True)  # 股票信息
    df = df.loc[start_date:end_date]

    # todo 提前筛选数据，加快速度
    b1 = (df['close'].shift(1) < df['open'].shift(1))
    # b2 = (df['close'].shift(1) > df['open'].shift(1) * 1.05)
    # b3 = (df['ma3'].shift(1) * 1.03 < df['ma7'].shift(1))
    b4 = df['change_pct'].shift(1) > 2
    b5 = df['ma20'].shift(1) > df['ma20'].shift(5)
    # 昨日最低点是5日内最低点
    b6 = df['low'].shift(1) == df['low'].rolling(window=5).min().shift(1)
    df['buy_signal'] = np.where(b1 & b4 & b5 & b6, 1, 0)
    return df


def print_profit_info(df):
    """
    输出每个股票盈利情况
    """
    global money, stock_count
    # 存储每个股票的盈亏情况
    a = money + stock_count * df['close'].iloc[-1]
    if a / 初始资金 == 1.0 or a is np.nan:
        pass
    elif a >= 初始资金:
        print(Fore.RED + stock_code[:6], end=': ')
        print((Fore.RED + str(round(a / 初始资金, 2))), end='  ')
        print('*' * int(float(round(a / 初始资金, 2) - 1) * 100))  # 显示星星
    elif a < 初始资金:
        print(Fore.GREEN + stock_code[:6], end=': ')
        print(Fore.GREEN + str(round(a / 初始资金, 2)), end='  ')
        print('*' * int(float(1 - round(a / 初始资金, 2)) * 100))  # 显示星星


def print_all_profit_info():
    """
    在最后输出整体的统计内容
    """
    global earnings
    win_sum = 0
    lost_sum = 0
    for w in earnings:
        if w > 0:
            win_sum += 1
        else:
            lost_sum += 1
    print(f"初始资金:{round(初始资金)}")
    print(f"剩余资金:{round(sum(earnings) + 初始资金, 2)}")
    print(f'盈利率:{round((sum(earnings) + 初始资金) / 初始资金 * 100, 2)}%', end='\n\n')
    # print(win_sum, len(earnings))
    print(f'胜率:{round(win_sum / len(earnings) * 100, 2)}%')
    print(f'次数:{len(earnings)}')
    print(f'盈利次数:{win_sum}')
    print(f'亏损次数:{lost_sum}')
    print(f"总盈亏:{round(sum(earnings), 2)}")
    print(f'平均每次盈利：{round(sum(earnings) / len(earnings), 2)}')
    wc = []  # 平均盈利
    lc = []  # 平均亏损
    for j in range(len(earnings)):
        if earnings[j] >= 0:
            wc.append(earnings[j])
        else:
            lc.append(earnings[j])
    print(f'盈利均值：{round(sum(wc) / len(wc), 2)}')
    print(f'亏损均值：{round(sum(lc) / len(lc), 2)}')
    earnings.sort()  # 排序
    # print(f'盈亏详情:{earnings}')


def back_test(stock_data, money):
    global old_money, stock_count, old_stock_money
    old_money = money  # 买入前记录资金状况
    stock_count = 0
    old_stock_money = 0
    for date in stock_data.index:  # 遍历所有日期
        # 卖出
        sell(stock_data, date)
        # 买入
        buy(stock_data, date)
    # 打印盈利情况
    print_profit_info(stock_data)


def plot_histogram(buy_date_count):
    # 将字典的键和值转换为列表
    # 将日期列表转换为Pandas的日期时间对象
    dates = [pd.to_datetime(date).strftime('%Y-%m-%d') for date in buy_date_count.keys()]
    counts = list(buy_date_count.values())
    # 创建一个Pandas Series对象，以便更容易地处理数据
    series = pd.Series(counts, index=dates)
    # series = series[series != 0]  # 过滤掉0
    # 绘制直方图
    plt.figure(figsize=(12, 6))  # 设置图表大小
    series.plot(kind='bar', color='skyblue', edgecolor='black')

    # 设置图表标题和轴标签
    plt.title('日期/购买次数直方图')
    plt.xlabel('Date')
    plt.ylabel('Count')

    # 旋转x轴标签，以便更容易阅读
    plt.xticks(rotation=90)

    # 显示图表
    plt.tight_layout()  # 调整布局以适应标签
    plt.show()


cpu_count = 24
earnings = []
low_date = None
high_date = None
indexdf = pd.read_csv(rf'../stock_data/daily_data/000001.XSHG.csv', index_col=0, parse_dates=True)
初始资金 = 100000
测试开始日期 = '2023-01-01'
测试结束日期 = '2024-01-01'
money = 初始资金
old_money = 0  # 买入前记录资金状况
stock_count = 0  # 买入股票数量
old_stock_money = 0  # 买入后存放股票市值
stock_code = None
buy_date_count = {}
sell_date_count = {}
# 追加日期维度的盈亏数据
date_list = pd.read_csv(f'../stock_data/date_list.csv')
date_list = date_list[(date_list['date'] >= 测试开始日期) & (date_list['date'] <= 测试结束日期)]
#
for date in date_list['date']:
    buy_date_count[date] = 0
    sell_date_count[date] = 0


def main():
    global money, stock_count, old_money, old_stock_money, stock_code
    stock_list = get_stock_list()
    for stock_code in stock_list.index:  # 遍历所有股票
        # print(stock_code)
        money = 初始资金
        df = get_buy_signal(stock_code, 测试开始日期, 测试结束日期)
        if df.shape[0] == 0:
            continue
        back_test(df, money)  # 回测
    print_all_profit_info()
    plot_histogram(buy_date_count)


if __name__ == '__main__':
    t = datetime.now()
    main()
    print(datetime.now() - t)
