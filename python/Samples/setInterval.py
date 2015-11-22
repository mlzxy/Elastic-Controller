import threading

def SetInterval(func, sec):
    def func_wrapper():
        SetInterval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t
