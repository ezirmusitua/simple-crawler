# -*- coding: utf-8 -*-  
import re
import uuid
import Queue
import random
import requests

random.seed()

# TODO: implement url patterm
UrlPattern = re.compile('(.*)<(\d+)-(\d+)>')

# TODO: make it makesense
CeilCount = 99999

def init():
    response = requests.get('https://www.baidu.com')
    if (response.ok):
        print "Gotcha"

def get_target_info(target_url):
    match_res = UrlPattern.match(target_url).groups()

    return (match_res[0], map(int, match_res[1:]))

def test_get_target_info():
    target_url = 'https://www.baidu.com/page?<0-100>'
    url_prefix, url_range = get_target_info(target_url)
    assert len(url_range) is 2, 'match should only have 3 element, but got %r' % len(url_range)
    assert isinstance(url_range[0], int), 'range floor should be integer'
    assert isinstance(url_range[1], int), 'range ceil should be integer'
    assert url_range[0] < url_range[1], 'range ceil should bigger than floor'
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

def handle_targets(targets):
    _target_dict, _url_pool, _page_pool = {}, {}, {}
    # TODO: add validation for targets
    for target in targets:
        # TODO: add validation for target
        target_uuid = generate_target_uuid(target)
        _page_pool[target_uuid] = [] 
        if 'next' not in target:
            url_prefix, url_range = get_target_info(target['url'])
            def _generator():
                __generator = (url_prefix + str(page_index) for page_index in range(url_range[0], url_range[1] + 1))
                return __generator.next()
            _target_dict[target_uuid] = { 'generator': _generator }
        else:
            _url_pool[target_uuid] = Queue.Queue()
            max_count = CeilCount if 'count' not in target else target['count']
            def _generator():
                return get_url_from_pool(target_uuid, _url_pool)
            _target_dict[target_uuid] = {
                'generator': _generator,
                'max_count': max_count
            }
        

    return _target_dict, _url_pool, _page_pool

def test_handle_targets():
    targets = [
        { 'url': 'https://www.baidu.com/page?<0-100>', 'uuid': 'test-uuid' },
        { 'url': 'https://www.baidu.com/page=<0-100>', 'next': '<a>(.*)</a>', 'count': 100, 'uuid': 'test-uuid-1'},
    ]
    test_url_pattern = re.compile('https://www.baidu.com/page?\d+')
    target_dict, url_pool, page_pool = handle_targets(targets)
    assert map(test_url_pattern.match, target_dict['test-uuid']['generator']()), 'result should match url pattern'
    assert isinstance(url_pool['test-uuid-1'], Queue.Queue), 'url pool should be instance of Queue'
    assert len(page_pool['test-uuid']) == len(page_pool['test-uuid-1']) == 0, 'init page pool should exist and empty'   
    print 'handle targets test all passed'

class Crawler(object):
    def __init__(self, targets):
        self.target_dict, self.url_pool, self.page_pool = handle_targets(targets)
        
    
    def use_headers(self, headers):
        pass

    def use_proxies(self, proxies):
        pass

    def start(self):
        _choices = self.target_dict.keys()
        while True:
            _cur_target = self.target_dict[random.choice(_choices)]
            target_url = _cur_target['generator']()
            # TODO: use Session
            # TODO: allow method choosen
            if (target_url != 'All Set'):
                response = requests.get(target_url)
                print response.text
            else:
                break

if __name__ == '__main__':
    test_get_target_info()
    test_get_url_from_pool()
    test_generate_target_uuid()
    test_handle_targets()
    targets = [
        {'uuid': 'test-uuid-1', 'url': 'https://www.baidu.com?page=<1-5>'},
        {'uuid': 'test-uuid-2', 'url': 'http://www.163.com?page=<1-5>'},
    ]
    crawler = Crawler(targets)
    crawler.start()
