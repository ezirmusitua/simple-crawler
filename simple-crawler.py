# -*- coding: utf-8 -*-  
import re
import requests

# TODO: implement url patterm
UrlPattern = re.compile('(.*)<(\d+)-(\d+)>')

# TODO: make it makesense
CeilCount = 99999

def init():
    response = requests.get('https://www.baidu.com')
    return response

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


def handle_targets(targets):
    _targets = []
    # TODO: add validation
    for target in targets:
        # generate uniq id for target generator
        if 'next' not in target:
            url_prefix, url_range = get_target_info(target['url'])
            _targets.append((url_prefix + str(page_index) for page_index in range(url_range[0], url_range[1] + 1)))
    return _targets

def test_handle_targets():
    targets = [
        { 'url': 'https://www.baidu.com/page?<0-100>' },
        { 'url': 'https://www.baidu.com/page=<0-100>' },
        { 'url': 'https://www.baidu.com/page=<0-100>', 'next': '<a>(.*)</a>', 'count': 100},
    ]
    test_url_pattern = re.compile('https://www.baidu.com/page?\d+')
    targets = handle_targets(targets)
    assert map(test_url_pattern.match, targets[0]), 'result should match url pattern'


def crawler(targets):
    _targets = handleTargets(targets)

if __name__ == '__main__':
    test_get_target_info()
    test_handle_targets()
    print init()