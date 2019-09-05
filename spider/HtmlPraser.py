# coding:utf-8
import base64
import config
from config import QQWRY_PATH, CHINA_AREA
from util.IPAddress import IPAddresss
import re
from util.compatibility import text_
from lxml import etree
class Html_Parser(object):
    '''html解析器'''
    def __init__(self):
        self.ips = IPAddresss(QQWRY_PATH)
    def parse(self, response, parser):
        '''解析方式选择'''
        if parser['type'] == 'xpath':
            return self.XpathPraser(response, parser)
        elif parser['type'] == 'regular':
            return self.RegularPraser(response, parser)
        elif parser['type'] == 'module':
            return getattr(self, parser['moduleName'], None)(response, parser)
        else:
            return None
    def AuthCountry(self, addr):
        '''判断国内国外'''
        for area in CHINA_AREA:
            if text_(area) in addr:
                return True
        return False
    def addrcut(self,addr):
        '''addr切割
            国内：省+市+服务/市+服务
            国外：地区+服务'''
        if text_('省') in addr or self.AuthCountry(addr):
            country = text_('国内')
            if '市' in addr:
                addr=addr.split('市')[0]
                if '省'in addr:
                    addr=addr.split('省')[1]
            else:
                addr = addr.split('省')[0]
        else:
            country = text_('国外')
            addr=text_('国外')
            # addr = addr.split(' ')[0]
        return country,addr
    def checkservice(self,addr):
        if ' ' in addr:
            a=''.join(addr.split(' ')[1:])
            if a:
                return a
        return '其他'
    def XpathPraser(self, response, parser):
        '''xpath方式解析'''
        proxylist = []
        root = etree.HTML(response)
        proxys = root.xpath(parser['pattern'])
        for proxy in proxys:
            try:
                ip = proxy.xpath(parser['position']['ip'])[0].text
                port = proxy.xpath(parser['position']['port'])[0].text
                t_way = 0
                protocol = 0
                addr = self.ips.getIpAddr(self.ips.str2ip(ip))
                t_service=self.checkservice(addr)
                country, addr=self.addrcut(addr)
            except Exception as e:
                continue
            proxy = {'ip': ip, 'port': int(port), 't_way': int(t_way), 'protocol': int(protocol), 'country': country,'t_service':t_service,'addr_id': addr,'attr':0,'score':0 }
            proxylist.append(proxy)
        return proxylist
    def RegularPraser(self, response, parser):
        '''正则表达式解析'''
        proxylist = []
        pattern = re.compile(parser['pattern'])
        matchs = pattern.findall(response)
        if matchs != None:
            for match in matchs:
                try:
                    ip = match[parser['position']['ip']]
                    port = match[parser['position']['port']]
                    t_way= 0
                    protocol = 0
                    addr = self.ips.getIpAddr(self.ips.str2ip(ip))
                    print(addr)
                    t_service = self.checkservice(addr)
                    country, addr = self.addrcut(addr)
                except Exception as e:
                    continue
                proxy = {'ip': ip, 'port': int(port), 't_way': int(t_way), 'protocol': int(protocol),'country': country, 't_service': t_service, 'addr_id': addr, 'attr': 0, 'score': 0}
                proxylist.append(proxy)
            return proxylist
    def CnproxyPraser(self, response, parser):
        '''端口号数据优化'''
        proxylist = self.RegularPraser(response, parser)
        chardict = {'v': '3', 'm': '4', 'a': '2', 'l': '9', 'q': '0', 'b': '5', 'i': '7', 'w': '6', 'r': '8', 'c': '1'}
        for proxy in proxylist:
            port = proxy['port']
            new_port = ''
            for i in range(len(port)):
                if port[i] != '+':
                    new_port += chardict[port[i]]
            new_port = int(new_port)
            proxy['port'] = new_port
        return proxylist
    def proxy_listPraser(self, response, parser):
        proxylist = []
        pattern = re.compile(parser['pattern'])
        matchs = pattern.findall(response)
        if matchs:
            for match in matchs:
                try:
                    ip_port = base64.b64decode(match.replace("Proxy('", "").replace("')", ""))
                    ip = ip_port.split(':')[0]
                    port = ip_port.split(':')[1]
                    t_way = 0
                    protocol = 0
                    addr = self.ips.getIpAddr(self.ips.str2ip(ip))
                    t_service = self.checkservice(addr)
                    country,addr=self.addrcut(addr)
                except Exception as e:
                    continue
                proxy = {'ip': ip, 'port': int(port), 't_way': int(t_way), 'protocol': int(protocol),'country': country, 't_service': t_service, 'addr_id': addr, 'attr': 0, 'score': 0}
                proxylist.append(proxy)
            return proxylist