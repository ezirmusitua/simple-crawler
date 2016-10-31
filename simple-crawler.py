# -*- coding: utf-8 -*-  
import re
import uuid
import json
import Queue
import random
import pprint
import requests

random.seed()

# TODO: implement url patterm
UrlPattern = re.compile('.*(https?://[^<>]*)')
# TODO: implement url patterm
RangePattern = re.compile('.*<(\d+)-(\d+)\/(\d+)>')

# TODO: make it make-sense
CeilCount = 99999

AllowedMethod = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTION']

def get_target_info(target_url):
    link_res = UrlPattern.match(target_url)
    link, start, end, step = '', 1, 1, 1
    if link_res != None:
        link = link_res.groups()[0]
    else:
        raise Error('url not found')
 
    range_res = RangePattern.match(target_url)
    if range_res != None:
        start, end, step = map(int, range_res.groups())

    return (link, start, end, step)

def test_get_target_info():
    target_url = 'https://www.baidu.com/page?<0-100/10>'
    url_prefix, start, end, step = get_target_info(target_url)
    assert isinstance(start, int), 'range floor should be integer'
    assert isinstance(end, int), 'range ceil should be integer'
    assert start < end, 'range ceil should bigger than floor'
    assert step > 0, 'range step should postive'
    print 'get target info test all passed'

def get_url_from_pool(target_uuid, pool):
    result = 'All Set'
    if not pool[target_uuid].empty():
        result = pool[target_uuid].get(False, 3000)
    return result 

def test_get_url_from_pool():
    target_uuid = 'test-uuid'
    pool = {'test-uuid': Queue.Queue()}
    assert get_url_from_pool(target_uuid, pool) == 'All Set', 'Empty pool return All Set'
    new_url = 'https://www.baidu.com'
    pool[target_uuid].put(new_url)
    assert get_url_from_pool(target_uuid, pool) == new_url, 'Not empty return url str'
    print 'get url from pool test all passed'

def generate_target_uuid(target):
    target_uuid = ''
    if 'uuid' not in target: 
        target_uuid = str(uuid.uuid1())
    else:
        target_uuid = target['uuid']
    return target_uuid

def test_generate_target_uuid():
    target_1 = {'uuid': 'test_uuid'}
    uuid_1 = generate_target_uuid(target_1)
    target_2 = {}
    uuid_2 = generate_target_uuid(target_2)

    assert uuid_1 == 'test_uuid', 'if has `uuid` should return uuid'
    assert uuid_2 != '' and uuid_2 != 'test_uuid' , 'if no `uuid` should return UUID str'
    print 'generate target uuid test all passed'

def handle_targets(target):
    _target, _url_pool, _page_pool = {}, {}, {}
    # TODO: add validation for targets
        # TODO: add validation for target
    _target_uuid = generate_target_uuid(target)
    _target['name'] = _target_uuid 
    _target['count'] = CeilCount if 'count' not in target else target['count']
    _target['pages'] = []
    _target['urls'] = Queue.Queue()
    # TODO: Extract follow to small method
    if 'next' not in target:
        _url_prefix, start, end, step = get_target_info(target['url'])
        if (start != end):
            _tmp = [_target['urls'].put(_url_prefix + str(page_index)) for page_index in range(start, end, step)]
        else:
            _tmp = [_target['urls'].put(_url_prefix) for i in range(0, _target['count'])]

    # TODO: use partial 
    _target['generator'] = _target['urls'].get
    # TODO: Add validation for method 
    if 'method' not in target:
        _target['method'] = 'GET'
    else:
        _target['method'] = target['method']
    # TODO: Add validation for params 
    if 'params' not in target:
        _target['params'] = None
    else:
        _target['params'] = target['params']
    # TODO: Add validation for data
    if 'data' not in target:
        _target['data'] = None
    else:
        _target['data'] = target['data']
    # TODO: Add validation for json
    if 'json' not in target:
        _target['json'] = None
    else:
        _target['json'] = target['json']
    return _target

def test_handle_targets():
    targets = [
        { 'url': 'https://www.baidu.com/page?<0-100/10>', 'uuid': 'test-uuid' },
        { 'url': 'https://www.baidu.com', 'next': 'None', 'count': 100, 'uuid': 'test-uuid-1'},
    ]
    test_url_pattern = re.compile('https://www.baidu.com/page?\d+')
    target_dict, url_pool, page_pool = handle_targets(targets)
    assert map(test_url_pattern.match, target_dict['test-uuid']['generator']()), 'result should match url pattern'
    assert isinstance(url_pool['test-uuid-1'], Queue.Queue), 'url pool should be instance of Queue'
    assert len(page_pool['test-uuid']) == len(page_pool['test-uuid-1']) == 0, 'init page pool should exist and empty'   
    print 'handle targets test all passed'

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
    return session.request(_method, url, params, data, json)

def test_create_session_obj():
    default_headers = {
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': '*/*',
        'User-Agent': 'python-requests/2.11.1'
    }
    test_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Host': 'localhost',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
    }
    test_proxies = {
        'http': 'http://127.0.0.1:8080',
        'https': 'https://127.0.0.1:8081'
    }
    s1 = create_session_obj(None, None)
    assert s1.headers == default_headers, 'not headers param then session headers should use default headers'
    assert s1.proxies == {}, 'not proxies param then session should use {}'
    s2 = create_session_obj(test_headers, test_proxies)
    assert s2.headers == test_headers, 'if give headers param then session headers should equal to given one'
    assert s2.proxies == test_proxies, 'if give proxies param then session proxies should equal to given one'
    print 'create session object test all passed'

class Crawler(object):
    def __init__(self, target, headers = None, proxies = None):
        self.session = create_session_obj(headers, proxies)
        self.target = handle_targets(target)
    
    def use_headers(self, headers):
        self.session.headers.update(headers)

    def use_proxies(self, proxies):
        self.session.proxies.update(proxies)

    def start(self):
        while not self.target['urls'].empty() and len(self.target['pages']) < self.target['count']:
            target_url = self.target['generator']()
            print '-', target_url
            # TODO: allow method choosen
            if (target_url != 'All Set'):
                response = request_by_session(self.session, self.target['method'], target_url,
                    self.target['params'], self.target['data'], self.target['json'])
                print response.content
                self.target['pages'].append(response.content)
    
    def get_page(self):
        return self.target['pages']

    def save(self):
        pass

def test_crawler():
    targets = [
        {'uuid': 'test-uuid-1', 'url': 'https://httpbin.org/headers?page=<1-5/1>', 'count': 1},
        {'uuid': 'test-uuid-2', 'url': 'https://httpbin.org/post', 'data': {'custname': 123}, 'method': 'POST', 'count': 1},
    ]
    crawler_1 = Crawler(targets[0])
    crawler_1.start()
    page_pool = crawler_1.get_page()
    assert len(page_pool) == 1, 'should get 1 pagem, actually %d' % len(page_pool)

    crawler_2 = Crawler(targets[1])
    crawler_2.start()
    page_pool = crawler_2.get_page()
    assert len(page_pool) == 1, 'should get 1 pagem, actually %d' % len(page_pool)

    # assert (map(lambda x: len(page_pool[x]) == 5, page_pool.keys()[:1])), 'page pool should store 5 page for per target'
    print 'crawler test all passed'

if __name__ == '__main__':
    # test_get_target_info()
    # test_get_url_from_pool()
    # test_generate_target_uuid()
    # test_handle_targets()
    # test_create_session_obj()
    test_crawler()
