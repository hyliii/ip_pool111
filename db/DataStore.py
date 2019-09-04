# coding:utf-8
import sys
from config import DB_CONFIG
from util.exception import Con_DB_Fail

try:
    if DB_CONFIG['DB_CONNECT_TYPE'] == 'pymongo':
        from db.MongoHelper import MongoHelper as SqlHelper
    elif DB_CONFIG['DB_CONNECT_TYPE'] == 'redis':
        from db.RedisHelper import RedisHelper as SqlHelper
    else:
        from db.SqlHelper import SqlHelper as SqlHelper
    sqlhelper = SqlHelper()
    sqlhelper.init_db()
except Exception as e:
    raise Con_DB_Fail
def store_data(queue2, db_proxy_num):
    '''
    读取队列中的数据，写入数据库中
    :param queue2:
    :return:
    '''
    successNum = 0
    failNum = 0
    while True:
        try:
            proxy = queue2.get(timeout=300)
            if proxy:
                from validator.Validator import getMyIP, detect_proxy,checkProxy
                selfip = getMyIP()
                ip = proxy['ip']
                port = proxy['port']
                proxies = {"http": "http://%s:%s" % (ip, port), "https": "https://%s:%s" % (ip, port)}
                # print(proxies)
                protocol, types, value2 = checkProxy(selfip, proxies,True)
                print(value2)
                if value2:
                    sqlhelper.insert(proxy,value2)
                    successNum += 1
            else:
                failNum += 1
            str = 'IPProxyPool----->>>>>>>>Success ip num :%d,Fail ip num:%d' % (successNum, failNum)
            sys.stdout.write(str + "\r")
            sys.stdout.flush()
        except BaseException as e:
            if db_proxy_num.value != 0:
                successNum += db_proxy_num.value
                db_proxy_num.value = 0
                str = 'IPProxyPool----->>>>>>>>Success ip num :%d,Fail ip num:%d' % (successNum, failNum)
                sys.stdout.write(str + "\r")
                sys.stdout.flush()
                successNum = 0
                failNum = 0