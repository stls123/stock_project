import multiprocessing as mp
import time


def pow(x):
    # 定义一个函数，计算输入参数的平方
    return x * x


def multicore():
    """使用 Pool 的 map 方法实现多进程并行计算。
    map 方法会自动分配任务给进程池中的进程，适合于对可迭代对象进行批量处理。
    """
    pool = mp.Pool(processes=2)  # 创建一个进程池，指定进程数量为2
    res = pool.map(pow, range(10000000))  # 使用 map 方法将 pow 函数应用于 range(10000000) 中的每个元素
    print(res)  # 打印结果列表


def multicore_apply():
    """使用 Pool 的 apply 方法实现多进程计算。
    apply 方法用于对单个参数进行处理，每次调用对应一个进程。
    apply_async 是 apply 的异步版本，允许设置回调函数，并且可以获取异步结果。
    """
    pool = mp.Pool(processes=2)  # 创建一个进程池，指定进程数量为2
    res = pool.apply_async(pow, (10,))  # 使用 apply_async 异步地将 pow 函数应用于参数10
    # 打印异步调用的结果，应使用 res.get() 来获取结果，而不是 print(res.get)
    print(res.get())  # 获取并打印异步计算的结果


if __name__ == '__main__':
    st_time = time.time()  # 记录开始时间
    multicore()  # 调用 multicore 函数进行多进程计算
    print("cost time:", time.time() - st_time)  # 计算并打印整个过程耗费的时间
