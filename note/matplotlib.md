
## matplotlib
### 导入
    from matplotlib import pyplot as plt

### 绘制折线图

#### 实例：绘制温度折线图
    # 可迭样式的x坐标
    x = range(2, 26, 2)
    # 列表类型的y坐标
    y = [15, 13, 14.5, 17, 20, 25, 26, 26, 24, 22, 18, 15]
    # 传入x, y坐标，通过调用plot方法绘制折线图
    plt.plot(x, y)
    # 显示折线图
    plt.show()

#### 设置图片大小和像素
    # 设置图片大小和像素
    # 这行放在最上面，相当于初始化，后面的图片都是这个格式
    fgn = plt.figure(figsize=(20, 8), dpi=80)

#### 保存为矢量图
    plt.savefig("./t1.png")

#### 设置x轴刻度， y轴刻度
    # 设置x轴刻度，传入的序列会变成x轴的刻度
    plt.xticks(x)
    # 设置y轴刻度，传入的序列会变成y轴的刻度
    plt.yticks( [ i for i in range(min(y), max(y)) ] )

    # 设置字符串类型的x轴刻度
    for i in range(20):
        x.append('hello' + str(i))

    # 设置字体旋转的读书（逆时针）
    plt.xticks(rotation=45)

#### 为 xy 轴和标题添加说明
    # 添加x轴说明
    plt.xlabel('time')
    # 添加y轴说明
    plt.ylabel('random.randint')
    # 添加标题
    plt.title('title')

#### 添加网格
    # 绘制网格
    plt.grid()
    # 设置透明度，最大为1
    plt.grid(alpha=0.4)
    # 设置网格样式
    plt.grid(linestyle='-')

#### 图形叠加
    # 想要图形叠加，就输出两次图形，y不同即可
    plt.plot(x, y1)
    plt.plot(x, y2)

#### 为不同线添加图例
    # 首先在绘制图形的时候写线条的说明
    plt.plot(x, y1, label='我的')
    plt.plot(x, y2, label='你的')
    # 然后添加图例,不加参数则会自动选择合适位置
    plt.legend()
    # 图例位置,loc设置为1~10是不同的位置
    plt.legend(loc=1)

#### 设置颜色和线形
    # 在调用plot的时候传入对应参数即可
    # color --> 线条颜色,对应颜色的单词即可，也可以是'#0000ff'十六进制字符串
    # linestyle --> 线条风格
        # - --> 实线
        # -- --> 点虚线
        # -. --> 点划线
        # : --> 纯虚线
        # '' --> 无线条
    # linewidth --> 线条粗细
    # alpha --> 透明度
    plt.plot(x, y, color='orange', linestyle='-', linewidth='5', alpha=0.4)

### 绘制散点图

    # 绘制散点图
    plt.scatter(x, y)