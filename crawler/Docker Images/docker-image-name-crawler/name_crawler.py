import selenium as se
from selenium import webdriver
import time
import requests
import os


class DockerImageNameCrawler():

    def __init__(self, url='http://10.0.0.15:8000', order='desc', **config_options):
        self.url = url
        self.order=order
        self.order_par=0 if order=='desc' else 10000000
        self.options = se.webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.driver = se.webdriver.Chrome(options=self.options)
        self.docker_hub_base_URL = 'https://hub.docker.com/search/?q=&type=image&operating_system=linux&architecture=amd64&page='
        self.docker_image_base_URL = 'https://hub.docker.com/r/'
        self.docker_hub_explore_URL='https://hub.docker.com/api/content/v1/products/search?q=&type=image&sort=updated_at&order={}&architecture=amd64&page='.format(self.order)
        self.__dict__.update(**config_options)
        self.session = requests.Session()
        self.cookie=self.get_cookie()
        self.update_cookie()
        self.session.headers=headers={'Host': 'hub.docker.com','Search-Version': 'v3','Accept': 'application/json','User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36','Referer': 'https://hub.docker.com/search/?q=&type=image&sort=updated_at&order=desc&page=16' ,'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8,ceb;q=0.7'}
        self.cookie_age=0
        
    def get_cookie(self):
        self.driver = se.webdriver.Chrome(options=self.options)
        self.driver.get(self.docker_hub_base_URL)
        self.driver.set_page_load_timeout(10)
        cookie=self.driver.get_cookies()
        self.driver.close()
        return cookie
    
    def update_cookie(self):
        c=requests.cookies.RequestsCookieJar()
        for item in self.cookie:
            c.set(item['name'],item['value'])
        self.session.cookies.update(c)
    
    def refresh_cookie(self):
        self.session = requests.Session()
        self.cookie=self.get_cookie()
        self.update_cookie()
        self.cookie_age=0
        
    def get(self,url):
        res=self.session.get(url).json()
        return res

    def crawl_image_name(self, pageNumber):
        docker_hub_URL = self.docker_hub_explore_URL + str(pageNumber)
        res=self.session.get(docker_hub_URL).json()
        image_dict={}
        if(not 'summaries' in res.keys()):
            return {}
        for i in range(len(res['summaries'])):
            original_id = (pageNumber - 1) * 25 + i + 1 + self.order_par
            image_dict[original_id] = res['summaries'][i]['name']
        return image_dict

    def crawl_image_name_task(self):
        while True:
            task_json = requests.get(self.url + '/get_image_name_task/').json()
            try:
                image_dict = self.crawl_image_name(task_json['page'])
            except:
                time.sleep(10)
            r = requests.post(self.url + '/image_name/',
                              json={'image_list': image_dict, 'page': task_json['page']})
            time.sleep(1)
            if(self.cookie_age>=100):
                self.refresh_cookie()

if __name__ == '__main__':
    posturl = os.getenv('POSTURL')
    order = os.getenv('ORDER')
    if(posturl == None):
        posturl = 'http://162.246.157.111:8000'
    if(order == None):
        order = 'desc'
    crawler = DockerImageNameCrawler(posturl,order)
    crawler.crawl_image_name_task()
