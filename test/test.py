# coding:utf-8
# import requests
# import json
# import re
# r = requests.get('http://127.0.0.1:8000/?types=0&count=5&country=中国')
# ip_ports = json.loads(r.text)
# print(ip_ports)
# ip = ip_ports[0][0]
# port = ip_ports[0][1]
# proxies = {
#     'http': 'http://%s:%s' % (ip, port),
#     'https': 'http://%s:%s' % (ip, port)
# }
# r = requests.get('http://www.baidu.com', proxies=proxies)
# r.encoding = 'utf-8'
# print(r.text)
# import random
# parserList=[0,1,2,3,5]
# p = random.randint(0,len(parserList))
# print(p)

# proxy = {'ip': '192.168.1.1', 'port': 80,'t_way':0, 'type': 0, 'protocol': 0, 'country': '中国', 'addr_id': '广州','t_service':'电信' ,'score':20,'attr':0}
# key='country'
# conditions={'country':'haha'}
# conditon_list=[]
# if proxy.get(key, None):
#     conditon_list.append(proxy.get(key) == conditions.get(key))
# proxy[proxy.get(key, None)] = conditions.get(key)
# print(proxy)
from db.DataStore import sqlhelper
k=[str(i[0])+':'+str(i[1]) for i in sqlhelper.select(10)]
print(k)
