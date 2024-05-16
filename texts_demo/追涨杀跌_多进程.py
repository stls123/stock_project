import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from tqdm import tqdm
import multiprocessing as mp

# 设置Pandas显示选项
pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 100)
pd.set_option('display.width', 1000)

# 设置matplotlib显示中文的配置
plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体为黑体
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号

# 全局变量
text_df = pd.DataFrame(
    {'code': [],
     'buy_date': [],
     'sell_date': [],
     'buy_price': [],
     'sell_price': [],
     'buy_type': [],
     'sell_type': []}
)

buy_date_count = {}  # 用来记录每个日期买入的次数
sell_date_count = {}  # 用来记录每个日期卖出的次数
earnings = []  # 用来记录每次交易的收益


def plot_histogram(buy_date_count):
    # 将字典的键和值转换为列表
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


def get_stock_list():
    """筛选股票数据"""
    # todo 没用到
    stock_df = pd.read_csv(r"../stock_data/stock_list.csv", index_col='code',
                           parse_dates=['start_date', 'end_date'])
    stock_df = stock_df[
        (stock_df.index.str[:3] != '688') &
        (stock_df.index.str[0] != '3') &
        (~stock_df['name'].str.contains('ST', na=False)) &
        (stock_df['start_date'] <= pd.to_datetime('2021-01-01')) &  # 逻辑上有一些疑问，安静的时候想想
        (stock_df['end_date'] >= pd.to_datetime('2024-01-01'))  # 逻辑上有一些疑问，安静的时候想想
        ]
    return stock_df


def set_date(start_date, end_date):
    global buy_date_count, sell_date_count
    date_list = pd.read_csv(f'../stock_data/date_list.csv')
    """ 为了后面做日期维度的交易次数的直方图,在这里完成了self.buy_date_count[d]， self.sell_date_count[d] 的初始化"""
    date_list = date_list[
        (date_list['date'] >= start_date) & (date_list['date'] <= end_date)]  # 筛选出测试的日期区间
    for d in date_list['date']:  # 相当于桶排序的初始化
        buy_date_count[d] = 0
        sell_date_count[d] = 0


class TradeBackTest(object):
    def __init__(self, money, stock_code, old_money, old_stock_money, 止盈, 止损, start_date, end_date):
        self.single_df = pd.DataFrame()
        self.stock_count = 0
        self.money = money  # 初始资金
        self.stock_code = stock_code  # 股票代码
        self.old_money = old_money  # 存放买入股票前的资金状况self.
        self.old_stock_money = old_stock_money  # 存放股票市值
        self.stop_profit_num = 止盈
        self.stop_loss_num = 止损
        self.start_date = start_date
        self.end_date = end_date

        self.indexdf = pd.read_csv(rf'../stock_data/daily_data/000001.XSHG.csv', index_col=0, parse_dates=True)

    def buy(self, date):
        global text_df, buy_date_count
        # todo 买入条件
        b0 = self.stock_count == 0 and self.single_df['buy_signal'].loc[date] == 1  # 没有持仓
        b6 = self.single_df['high'].loc[date] >= self.single_df['high'].iloc[
            self.single_df.index.get_loc(date) - 1]
        if b0 and b6:
            text_df = text_df.append({'code': self.stock_code}, ignore_index=True)  # 添加新行
            text_df.iloc[-1, text_df.columns.get_loc('buy_date')] = date.strftime('%Y-%m-%d')  # 记录买入日期数据
            buy_date_count[date.strftime('%Y-%m-%d')] += 1  # 记录当前日期买入一次
            buy_price = max(self.single_df['high'].iloc[self.single_df.index.get_loc(date) - 1],
                            self.single_df['open'].loc[date])  # 计算买入价
            text_df.iloc[-1, text_df.columns.get_loc('buy_price')] = buy_price
            self.old_money = self.money  # 买入前记录资金状况
            self.stock_count = (self.money // (buy_price * 100)) * 100  # 增加股票数量
            self.money -= self.stock_count * buy_price  # 减少资金数量
            self.old_stock_money = self.stock_count * buy_price  # 买入后存放股票市值
            text_df.iloc[-1, text_df.columns.get_loc('buy_type')] = '创新高买入'

    def sell(self, date):
        global earnings
        # todo 设置止盈止损点位
        # 止盈条件：20个点止盈
        stop_profit = self.single_df['high'].loc[date] * self.stock_count >= self.old_stock_money * (
                (100 + self.stop_profit_num) / 100)
        # 止损条件：5个点止损
        stop_loss = (self.single_df['low'].loc[date] * self.stock_count <= self.old_stock_money * (
                100 - self.stop_loss_num) / 100 <
                     self.single_df['open'].loc[date] * self.stock_count)
        # 开盘止损：5个点止损
        open_stop_loss = self.single_df['open'].loc[date] * self.stock_count <= self.old_stock_money * (
                100 - self.stop_loss_num) / 100
        # 开盘止盈：20个点止盈
        open_stop_profit = self.single_df['open'].loc[date] * self.stock_count >= self.old_stock_money * (
                100 + self.stop_profit_num) / 100
        # 移动止损（止损线每天向上移动）
        move_stop = self.single_df['low'].loc[date] <= self.single_df['low'].iloc[
            self.single_df.index.get_loc(date) - 1] < self.single_df['open'].loc[date]
        # 开盘移动止损
        open_move_loss = self.single_df['open'].loc[date] <= self.single_df['low'].iloc[
            self.single_df.index.get_loc(date) - 1]
        if self.stock_count != 0:
            if open_stop_loss or open_stop_profit or open_move_loss:  # 开盘止损 开盘止盈 开盘移动止损
                text_df.iloc[-1, text_df.columns.get_loc('sell_date')] = date.strftime('%Y-%m-%d')
                text_df.iloc[-1, text_df.columns.get_loc('sell_price')] = self.single_df['open'].loc[date]
                text_df.iloc[-1, text_df.columns.get_loc('sell_type')] = '开盘卖出'
                self.money += self.single_df['open'].loc[date] * self.stock_count - 20
                self.stock_count = 0
                earnings.append(round(self.money - self.old_money, 2))
            elif stop_loss:  # 止损点卖出
                text_df.iloc[-1, text_df.columns.get_loc('sell_date')] = date.strftime('%Y-%m-%d')  # 记录卖出日期数据
                text_df.iloc[-1, text_df.columns.get_loc('sell_price')] = round(
                    (self.old_stock_money * ((100 - self.stop_loss_num) / 100)) / self.stock_count, 2)
                text_df.iloc[-1, text_df.columns.get_loc('sell_type')] = '止损卖出'
                self.money += self.old_stock_money * ((100 - self.stop_loss_num) / 100) - 20
                self.stock_count = 0
                earnings.append(round(self.money - self.old_money, 2))
            elif stop_profit:  # 止盈点卖出
                text_df.iloc[-1, text_df.columns.get_loc('sell_date')] = date.strftime('%Y-%m-%d')  # 记录卖出日期数据
                text_df.iloc[-1, text_df.columns.get_loc('sell_price')] = round(
                    (self.old_stock_money * ((100 + self.stop_profit_num) / 100)) / self.stock_count, 2)
                text_df.iloc[-1, text_df.columns.get_loc('sell_type')] = '止盈卖出'
                self.money += self.old_stock_money * ((100 + self.stop_profit_num) / 100) - 20
                self.stock_count = 0
                earnings.append(round(self.money - self.old_money, 2))
            elif move_stop:  # 移动止损
                text_df.iloc[-1, text_df.columns.get_loc('sell_date')] = date.strftime('%Y-%m-%d')  # 记录卖出日期数据
                text_df.iloc[-1, text_df.columns.get_loc('sell_price')] = round(
                    self.single_df['low'].iloc[self.single_df.index.get_loc(date) - 1],
                    2)
                text_df.iloc[-1, text_df.columns.get_loc('sell_type')] = '止损卖出'
                self.money += self.single_df['low'].iloc[self.single_df.index.get_loc(date) - 1] * self.stock_count - 20
                self.stock_count = 0
                earnings.append(round(self.money - self.old_money, 2))

    def get_buy_signal(self):
        """
        num:从哪个位置开始获取前面的数据
        count:获取几个数据（从第i个位置获取数据）
        """
        self.single_df = pd.read_csv(fr"../stock_data/daily_data/{self.stock_code}.csv", index_col=0,
                                     parse_dates=True)  # 股票信息
        self.single_df = self.single_df.loc[self.start_date:self.end_date]

        # todo 提前筛选数据，快速度  ==> 考虑换成self.df
        b1 = (self.single_df['close'].shift(1) > self.single_df['open'].shift(1))
        b3 = self.single_df['l_ma3'].shift(2) * 1.03 < self.single_df['l_ma7'].shift(2)
        b4 = self.single_df['net_pct_xl'].shift(1) + self.single_df['net_pct_main'].shift(1) > 20
        b5 = self.single_df['open'].shift(1) <= self.single_df['low'].shift(2)
        self.single_df['buy_signal'] = np.where(b1 & b3 & b4 & b5, 1, 0)

    def back_test(self):
        self.old_money = self.money  # 买入前记录资金状况
        self.stock_count = 0  # 股票数量归零
        self.old_stock_money = 0  # 股票市值归零

        for d in self.single_df.index:  # 遍历所有日期
            # 卖出
            self.sell(d)
            # 买入
            self.buy(d)


def print_text_info(money, 测试开始日期, 测试结束日期, 止盈, 止损):
    print('初始资金：', money, '\n开始日期：', 测试开始日期, '\n结束日期：', 测试结束日期, '\n止盈：', 止盈, '%', '\n止损：',
          止损, '%')


def print_all_profit_info(初始资金, earnings):
    """
    在最后输出整体的统计内容
    """
    global buy_date_count
    win_sum = 0
    lost_sum = 0
    for w in earnings:
        if w > 0:
            win_sum += 1
        else:
            lost_sum += 1
    print(f"剩余资金:{round(sum(earnings) + 初始资金, 2)}")
    print(f'盈利率:{round((sum(earnings) + 初始资金) / 初始资金 * 100, 2)}%', end='\n\n')
    print(f'次数:{len(earnings)}')
    print(f'盈利次数:{win_sum}')
    print(f'亏损次数:{lost_sum}')
    print(f'胜率:{round(win_sum / len(earnings) * 100, 2)}%')
    print(f"总盈亏:{round(sum(earnings), 2)}")
    print(f'平均每次盈亏值：{round(sum(earnings) / len(earnings), 2)}')
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
    # 追加盈利百分比到text_df中
    text_df['profit_pct'] = round((text_df['sell_price'] - text_df['buy_price']) / text_df['buy_price'] * 100, 2)
    # 显示结果
    print(text_df)
    print(text_df.describe())
    # 画图
    plot_histogram(buy_date_count)


测试开始日期 = '2023-01-01'
测试结束日期 = '2024-01-01'
止盈 = 1000
止损 = 2000
初始资金 = 100000


def main(stk_l):
    set_date(测试开始日期, 测试结束日期)

    for stock_code in tqdm(stk_l):  # 遍历所有股票
        TBT = TradeBackTest(money=初始资金, stock_code=stock_code, old_money=0, old_stock_money=0,
                            止盈=止盈,
                            止损=止损, start_date=测试开始日期, end_date=测试结束日期)
        TBT.get_buy_signal()
        if TBT.single_df.shape[0] == 0:
            continue
        text_df = TBT.back_test(text_df)  # 回测

    print_all_profit_info(初始资金, earnings)  # 输出测试后的总体结果


# 多进程
def multi_course():
    q = mp.Queue()
    stock_list = get_stock_list()  # 获取股票列表并筛选
    print_text_info(初始资金, 测试开始日期, 测试结束日期, 止盈, 止损)  # 显示测试的一些内容
    task_list = []
    cpu_count = mp.cpu_count()
    task_id = 0
    for i in range(cpu_count):
        task_list.append(list(stock_list[task_id:task_id + len(stock_list) // cpu_count].index))
        task_id += len(stock_list) // cpu_count
    print(f'cpu_count:{cpu_count}')
    print(list(task_list))
    pool = mp.Pool(processes=cpu_count)
    pool.map(main, args=(task_list, q))
    pool.close()
    pool.join()


if __name__ == '__main__':
    t = datetime.now()
    multi_course()
    print('代码执行用时：', datetime.now() - t)
