import multiprocessing as mp


def worker(lock, i):
    # 当工作需要互斥的时候使用lock锁
    with lock:
        print(f'Worker {i} is running')


if __name__ == '__main__':
    lock = mp.Lock()  # 创建一个锁对象
    processes = []

    for i in range(5):
        # mp.Process 是 multiprocessing 模块中的一个类，用于创建新的进程。
        p = mp.Process(target=worker, args=(lock, i))  # 将锁对象作为参数传递给worker函数
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    print('All workers have finished')

    # 输出结果：
    # Worker 0 is running
    # Worker 1 is running
    # Worker 2 is running
    # Worker 3 is running
    # Worker 4 is running
    # All workers have finished

    # 可以看到，多个进程在执行时会按照顺序依次执行，不会出现同时执行的情况。
    # 需要注意的是，锁对象需要在每个进程中共享，否则会引发错误。
    # 另外，锁对象还可以用来保护共享资源，避免多个进程同时访问和修改同一个资源。
