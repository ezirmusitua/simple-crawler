# -*- coding: utf-8 -*-  
import re
import requests

# TODO: implement url patterm
RangePattern = re.compile('.*<(\d+)-(\d+)>')

def init():
    response = requests.get('https://www.baidu.com')
    return response

def get_target_range(target_url):
    match_res = RangePattern.match(target_url)
    print match_res.groups()
    return tuple(map(int, match_res.groups()))

def test_get_target_range():
    target_url = 'https://www.baidu.com/page?<0-100>'
    page_range = get_target_range(target_url)
    assert len(page_range) is 2
    assert isinstance(page_range[0], int)
    assert isinstance(page_range[1], int)
    assert page_range[0] < page_range[1]


def handle_targets(targets):
    return targets

def test_handle_targets():
    pass


def crawler(targets):
    _targets = handleTargets(targets)

if __name__ == '__main__':
    test_get_target_range()
    test_handle_targets()
    print init()