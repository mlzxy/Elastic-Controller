import requests
import json
def Http_Request(addr,data):
    return requests.post(addr, data = json.dumps(data), headers={'content-type': 'application/json'})

r = Http_Request('http://127.0.0.1:9200/stat',{'data':1})    
print r, r.text
