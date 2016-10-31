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

def get_url_from_pool(target_uuid, pool):
    result = 'All Set'
    if not pool[target_uuid].empty():
        result = pool[target_uuid].get(False, 3000)
    return result 

def generate_target_uuid(target):
    target_uuid = ''
    if 'uuid' not in target: 
        target_uuid = str(uuid.uuid1())
    else:
        target_uuid = target['uuid']
    return target_uuid

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
    return session.request(_method, url, params, data, json, timeout = 5)

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
