import datetime
# 直接获取大哥前时间
s = datetime.datetime.now()

# 按照不同周期分解时间
year = s.year
month = s.month
day = s.day
hour = s.hour
minute = s.minute
second = s.second

# 按格式取对应值
print(s.strftime("%Y-%m-%d %H:%M:%S"))