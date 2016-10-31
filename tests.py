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
    print 'crawler test all passed'

def test_get_target_info():
    target_url = 'https://www.baidu.com/page?<0-100/10>'
    url_prefix, start, end, step = get_target_info(target_url)
    assert isinstance(start, int), 'range floor should be integer'
    assert isinstance(end, int), 'range ceil should be integer'
    assert start < end, 'range ceil should bigger than floor'
    assert step > 0, 'range step should postive'
    print 'get target info test all passed'


def test_get_url_from_pool():
    target_uuid = 'test-uuid'
    pool = {'test-uuid': Queue.Queue()}
    assert get_url_from_pool(target_uuid, pool) == 'All Set', 'Empty pool return All Set'
    new_url = 'https://www.baidu.com'
    pool[target_uuid].put(new_url)
    assert get_url_from_pool(target_uuid, pool) == new_url, 'Not empty return url str'
    print 'get url from pool test all passed'


def test_generate_target_uuid():
    target_1 = {'uuid': 'test_uuid'}
    uuid_1 = generate_target_uuid(target_1)
    target_2 = {}
    uuid_2 = generate_target_uuid(target_2)

    assert uuid_1 == 'test_uuid', 'if has `uuid` should return uuid'
    assert uuid_2 != '' and uuid_2 != 'test_uuid' , 'if no `uuid` should return UUID str'
    print 'generate target uuid test all passed'


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
