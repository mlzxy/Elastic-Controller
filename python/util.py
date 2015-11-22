import threading
import requests
import json


def Set_Interval(func, sec):
    def func_wrapper():
        Set_Interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


def Http_Request(addr,data):
    return requests.post(addr, data = json.dumps(data), headers={'content-type': 'application/json'})

    

    
