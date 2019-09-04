# coding:utf-8
import sys
PY3 = sys.version_info[0] == 3
if PY3:
    text_type = str
    binary_type = bytes
else:
    text_type = unicode #防止报错，用于Python2.7解释器，系统中Python在未配置状态下默认为2.7版本
    binary_type = str
def text_(s, encoding='utf-8', errors='strict'):
    if isinstance(s, binary_type):
        return s.decode(encoding, errors)
    return s
def bytes_(s, encoding='utf-8', errors='strict'):
    if isinstance(s, text_type):
        return s.encode(encoding, errors)
    return s
