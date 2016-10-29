# -*- coding: utf-8 -*-  
import re
import requests

def init():
    response = requests.get('https://www.baidu.com')
    return response

if __name__ == '__main__':
    print init()