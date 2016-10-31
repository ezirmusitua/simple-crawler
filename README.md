## A Simple Crawler  
Crawl data simple  

## How to use  
Write your .py file    
```python  
import Crawler from simple_crawler  

targets = [
    { 'url': 'http://example.com', 'next': '<a href="(.*)">(.*)</a>', 'max': 100, 'method': 'GET'},
    { 'url': 'http://example.com/list?page=<0-100>'},
    { 'url': 'http://example.com/list?page=<0-100>', 'uuid': 'test'}
]

crawler = Crawler = [targets[0]]
crawler.start()
pages = crawler.get_page()

print pages.length
```  
Do some simple decoration  
```python  
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
}

crawler.use_headers(headers);

proxies = {
  "http": "http://127.0.0.1:8080",
  "https": "http://127.0.0.1:1080",
}

crawler.use_proxies(proxies);
```  

## How to install  
pip instal simple-crawler

## TODOs
 - [ ] Implement extract `next` from page and store to queue
 - [x] Use Session of requests and allow using other METHOD  
 - [x] Implement `use_headers` and `use_proxies` method
 - [x] Add crawl time gap
 - [ ] Use gevent
 - [ ] add expection handler
 - [ ] Add method to set timeout of request
 - [ ] Update url constructor, use format not concat
 - [x] Implement `save` method that use to save page to json file
 - [ ] Implement post template parser
 - [ ] Check why previous implemention was wrong
 - [ ] Rewrite all tests