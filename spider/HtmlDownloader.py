# coding:utf-8
import random
import config
from db.DataStore import sqlhelper
import requests
import chardet
class Html_Downloader(object):
    @staticmethod
    def download(url):
        proxylist = sqlhelper.select(10)
        if not proxylist:
            proxies=None
        else:
            proxy = random.choice(proxylist)
            proxies = {"http": "http://%s:%s" % ( proxy[0], proxy[1]), "https": "http://%s:%s" % ( proxy[0], proxy[1])}
        try:
            r = requests.get(url=url, headers=config.get_header(),proxies=proxies, timeout=config.TIMEOUT)
            r.encoding = chardet.detect(r.content)['encoding']
            if (not r.ok) or len(r.content) < 500:
                raise ConnectionError
            else:
                return r.text
        except Exception as e:
            count = 0  # 已重试次数
            proxylist = sqlhelper.select(10)
            if not proxylist:
                return None
            while count < config.RETRY_TIME:
                try:
                    proxy = random.choice(proxylist)
                    proxies = {"http": "http://%s:%s" % ( proxy[0], proxy[1]), "https": "http://%s:%s" % ( proxy[0], proxy[1])}
                    r = requests.get(url=url, headers=config.get_header(), timeout=config.TIMEOUT, proxies=proxies)
                    r.encoding = chardet.detect(r.content)['encoding']
                    if (not r.ok) or len(r.content) < 500:
                        raise ConnectionError
                    else:
                        return r.text
                except Exception:
                    count += 1
        return None