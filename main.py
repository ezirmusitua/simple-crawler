# -*- coding: utf-8 -*-  
import re
import uuid
import time
import json
import Queue
import codecs   
import random
import pprint
import functools
import gevent
import requests


random.seed()

# TODO: implement url pattern
UrlPattern = re.compile('.*(https?://.*)')
# TODO: implement url pattern
RangePattern = re.compile('.*<(\d+)-(\d+)\/(\d+)>')

# TODO: make it make-sense
CeilCount = 9999

AllowedMethod = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTION']

def get_target_info(target_url):
    link_res = UrlPattern.match(target_url)
    link, start, end, step = '', 1, 1, 1
    if link_res != None:
        link = link_res.groups()[0]
    else:
        raise Exception('url not found')
 
    range_res = RangePattern.match(target_url)
    if range_res != None:
        start, end, step = map(int, range_res.groups())

    return (link, start, end, step)

def get_url_from_pool(target_uuid, pool):
    result = 'All Set'
    if not pool[target_uuid].empty():
        result = pool[target_uuid].get(False, 3000)
    return result 

def get_target_name(target):
    target_uuid = ''
    if 'name' not in target: 
        target_uuid = str(uuid.uuid1())
    else:
        target_uuid = target['name']
    return target_uuid

def get_target_count(target, max_count = 1):
    return target['count'] if 'count' in target else max_count

def get_range_info(target):
    _range = target['range']
    _from, _to, _step = 0, CeilCount, 1
    if ('from' in _range):
        _from = _range['from']
    if ('to' in _range):
        _to = _range['to']
    if ('step' in _range):
        _step = _range['step']
    return (_from, _to, _step)

def get_target_method(target, default_method = 'GET'):
    return target['method'] if 'method' in target else default_method

def get_target_params(target): 
    return target['params'] if 'params' in target else None

def get_target_data(target): 
    return target['data'] if 'data' in target else None

def get_target_json(target): 
    return target['json'] if 'json' in target else None

def get_target_next_url(target):
    if ('range' in target and 'pattern' in target):
        raise Exception('`range` and `pattern` can not exist at same time')
    _generator = None
    if ('range' in target):
        _from, _to, _step = get_range_info(target)
        def _url_generator():
            _range_list = range(_from, _to, _step)
            for page_index in _range_list:
                yield target['url'] % page_index
        _generator = _url_generator().next
    if ('pattern' in target):
        # TODO: timeout to constant
        _generator = functools.partial(target['urls'].get, blocked = false, timeout = 5)
    return _generator


def handle_target(target):
    _target = {}
    # TODO: add validation for target
    target['urls'] = Queue.Queue()
    _target['pages'] = []
    _target['name'] = get_target_name(target)
    _target['count'] = get_target_count(target, CeilCount)
    _target['method'] = get_target_method(target)
    _target['params'] = get_target_params(target)
    _target['data'] = get_target_data(target)
    _target['json'] = get_target_json(target)
    _target['next-url'] = get_target_next_url(target)
    return _target

def test_handle_target():
    target_1 = {
        'url': 'https://www.baidu.com?page=%d&page-size=100',
        'range': { 'end': 50 }
    }
    target = handle_target(target_1)
    print target['next-url']()
    target_2 = {
        'url': 'https://www.baidu.com',
        'pattern': 'abc'
    }

def create_session_obj(headers, proxies):
    session = requests.Session()
    if headers is not None:
        session.headers.update(headers)
    if proxies is not None:
        session.proxies.update(proxies)
    return session

def request_by_session(session, method, url, params = None, data = None, json = None):
    _method = 'GET'
    if AllowedMethod.index(method.upper()) > -1:
        _method = method.upper()
    # TODO: Add validation for url
    try:
        return session.request(_method, url, params, data, json, timeout = 5)
    except Exception:
        return {content: 'requests error happend!'} 

class Crawler(object):
    def __init__(self, target, headers = None, proxies = None, sleep_time = 0):
        self.session = create_session_obj(headers, proxies)
        self.target = handle_targets(target)
        self.sleep_time = sleep_time
    
    def use_headers(self, headers):
        self.session.headers.update(headers)

    def use_proxies(self, proxies):
        self.session.proxies.update(proxies)

    def use_sleep_time(self, sleep_time):
        self.sleep_time = sleep_time

    def start(self):
        while not self.target['urls'].empty() and len(self.target['pages']) < self.target['count']:
            target_url = self.target['generator']()
            print '-', target_url
            # TODO: allow method choosen
            if (target_url != 'All Set'):
                response = request_by_session(self.session, self.target['method'], target_url,
                    self.target['params'], self.target['data'], self.target['json'])
                self.target['pages'].append(response.content)
            # TODO: use function
            time.sleep(self.sleep_time)
    
    def get_page(self):
        return self.target['pages']

    def save(self):
        # TODO: allow custom
        with codecs.open('data/' + self.target['name'] + '.json', 'wb', 'utf-8') as wf:
            # TODO: allow use filter function
            json.dump(self.target['pages'], wf)

if __name__ == '__main__':
    test_handle_target()