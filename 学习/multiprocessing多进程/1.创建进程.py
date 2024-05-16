import multiprocessing as mp  # mul ti pro ces sing


def job(a, b):
    for i in range(a):
        a += b
        print(a)


if __name__ == '__main__':
    p1 = mp.Process(target=job, args=(1, 2))  # 创建进程对象, 注意参数中的函数是没有括号的，因为是引用，不是调用
    p1.start()  # 启动进程
    p1.join()  # 等待进程结束
