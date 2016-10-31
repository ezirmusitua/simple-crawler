## A Simple Crawler  
Crawl data simple  

## How to use  
Write your .py file    
```python  
import crawler from simple_crawler  

targets = [
    { 'url': 'http://example.com', 'next': '<a href="(.*)">(.*)</a>', 'max': 100, 'method': 'GET'},
    { 'url': 'http://example.com/list?page=<0-100>'},
    { 'url': 'http://example.com/list?page=<0-100>', 'uuid': 'test'}
]

results = crawler.start(targets)

print results[0].length
print results[1].length
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
 - [ ] Use Session of requests and allow using other METHOD  
 - [ ] Implement `use_headers` and `use_proxies` method
 - [ ] Implement `save` method that use to save page to json file
 - [ ] Check why previous implemention was wrong
 - [ ] Rewrite all tests