import queue
# 队列可以有序的安排问题
q = queue.Queue()
for i in range(10):
    q.put(i)

while not q.empty():
    print(q.get(), end=' ')

# 输出结果：0 1 2 3 4 5 6 7 8 9
# 输出结果：数据会按照放进去的顺序拿出来
