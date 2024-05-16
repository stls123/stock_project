# 读取腾讯文档的数
import requests

# 腾讯文档的API地址
url = 'https://api.wj.qq.com/cgi-bin/data/conditionget?t=xxxxxxxxxxx'

# 替换xxxxxxxxxxx为你的腾讯文档的ID

# 发送GET请求
response = requests.get(url)