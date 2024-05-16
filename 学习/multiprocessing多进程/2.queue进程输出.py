import multiprocessing as mp


def worker(q):
    sum = 0
    for i in range(100):
        sum += i
    q.put(sum)  # 将数据放入队列


if __name__ == '__main__':
    q = mp.Queue()  # 创建一个进程队列
    p1 = mp.Process(target=worker, args=(q,))  # args如果只有一个，需要加一个逗号，因为它是元组
    p2 = mp.Process(target=worker, args=(q,))  # args如果只有一个，需要加一个逗号，因为它是元组
    p2.start()
    p1.start()
    p1.join()
    p2.join()
    print(q.get())
    print(q.get())
