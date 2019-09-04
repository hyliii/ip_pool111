# coding:utf-8
import sys
import chardet
import gevent
from gevent import monkey
monkey.patch_all()
import json
import os
import requests
import time
import psutil
from multiprocessing import Process, Queue
import config
from db.DataStore import sqlhelper
from util.exception import Test_URL_Fail
'''检测器'''
def validator(queue1, queue2, myip):
    tasklist = []
    proc_pool = {}     # 所有进程列表
    cntl_q = Queue()   # 控制信息队列
    while True:
        if not cntl_q.empty():# 处理已结束的进程
            try:
                pid = cntl_q.get()
                proc = proc_pool.pop(pid)
                proc_ps = psutil.Process(pid)
                proc_ps.kill()
                proc_ps.wait()
            except Exception as e:
                pass
        try:
            if len(proc_pool) >= config.MAX_CHECK_PROCESS:
                time.sleep(config.CHECK_WATI_TIME)
                continue
            proxy = queue1.get()
            tasklist.append(proxy)
            if len(tasklist) >= config.MAX_CHECK_CONCURRENT_PER_PROCESS:
                p = Process(target=process_start, args=(tasklist, myip, queue2, cntl_q))
                p.start()
                proc_pool[p.pid] = p
                tasklist = []
        except Exception as e:
            if len(tasklist) > 0:
                p = Process(target=process_start, args=(tasklist, myip, queue2, cntl_q))
                p.start()
                proc_pool[p.pid] = p
                tasklist = []
def process_start(tasks, myip, queue2, cntl):
    spawns = []
    for task in tasks:
        spawns.append(gevent.spawn(detect_proxy, myip, task, queue2))
    gevent.joinall(spawns)
    cntl.put(os.getpid())  # 子进程退出是加入控制队列
def detect_proxy(selfip, proxy,queue2=None):
    ip = proxy['ip']
    port = proxy['port']
    proxies = {"http": "http://%s:%s" % (ip, port), "https": "https://%s:%s" % (ip, port)}
    protocol, types = getattr(sys.modules[__name__],config.CHECK_PROXY['function'])(selfip, proxies)#checkProxy(selfip, proxies)
    if protocol >=0:
        proxy['protocol'] = protocol
        proxy['attr'] = types
    else:
        proxy = None
    if queue2:
        queue2.put(proxy)
    return proxy
def detect_from_db(myip, proxy, proxies_set):
    proxy_dict = {'ip': proxy[0], 'port': proxy[1]}
    result1 = detect_proxy(myip, proxy_dict)
    if result1:
        proxy_str = '%s:%s' % (proxy[0], proxy[1])
        proxies_set.add(proxy_str)
    else:
        if proxy[2] < 1:
            sqlhelper.delete({'ip': proxy[0], 'port': proxy[1]})
        else:
            score = proxy[2]-1
            sqlhelper.update({'ip': proxy[0], 'port': proxy[1]}, {'score': score})
            proxy_str = '%s:%s' % (proxy[0], proxy[1])
            proxies_set.add(proxy_str)
def checkProxy(selfip, proxies):
    http, http_types= _checkHttpProxy(selfip, proxies,True)
    https, https_types= _checkHttpProxy(selfip, proxies)
    if http and https:
        protocol = 2
        types = http_types
    elif http:
        types = http_types
        protocol = 0
    elif https:
        types = https_types
        protocol = 1
    else:
        types = -1
        protocol = -1
    return protocol,types
def _checkHttpProxy(selfip, proxies, isHttp=False):
    types = -1
    if isHttp:
        test_url = config.GOAL_HTTP_LIST
    else:
        test_url = config.GOAL_HTTPS_LIST
    try:
        r = requests.get(url=test_url[0], headers=config.get_header(), timeout=config.TIMEOUT, proxies=proxies)
        if r.ok:
            content = json.loads(r.text)
            headers = content['headers']
            ip = content['origin']
            proxy_connection = headers.get('Proxy-Connection', None)
            if ',' in ip:
                types = 2
            elif proxy_connection:
                types = 1
            else:
                types = 0
            return True, types
        else:
            return False, types
    except Exception as e:
        return False, types
def checkSped(selfip, proxy):
    try:
        speeds = []
        test_url = config.GOAL_HTTPS_LIST
        proxies = {"http": "http://%s:%s" % (proxy['ip'], proxy['port']), "https": "https://%s:%s" % (proxy['ip'], proxy['port'])}
        for i in test_url:
            try:
                start = time.time()
                r = requests.get(url=i, headers=config.get_header(), timeout=config.TIMEOUT, proxies=proxies)
                if r.ok:
                    speed = round(int(time.time() - start),2)
                    speeds.append(speed)
                else:
                    speeds.append(1000000)
            except Exception as e:
                speeds.append(1000000)
        return speeds
    except Exception as e:
        return  None
def getMyIP():
    try:
        r = requests.get(url=config.TEST_IP, headers=config.get_header(), timeout=config.TIMEOUT)
        ip = json.loads(r.text)
        return ip['origin']
    except Exception as e:
        raise Test_URL_Fail
if __name__ == '__main__':
    ip = '222.186.161.132' 
    port = 3128
    proxies = {"http": "http://%s:%s" % (ip, port), "https": "http://%s:%s" % (ip, port)}
    _checkHttpProxy(None,proxies)