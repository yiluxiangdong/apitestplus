import timeit
import profile

def square(x):
    return x*x+2

def do():
    obj = [1,2,3,4,5]
    list(map(square, obj))

def  perf_analysis():
    #查看函数耗时
    t = timeit.Timer(setup='from __main__ import do', stmt='do()')
    print(t.timeit())
    #函数进行性能分析
    profile.run('do()')

if __name__ == '__main__':
    perf_analysis()