import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import requests
import logging 
import selenium
import datetime as dt
import re
from bs4 import BeautifulSoup
import time
import math
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from tqdm import tqdm
from multiprocessing import Pool
from utils.constants import *


import requests
import logging 
import selenium
import re
import datetime as dt
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup
import time
import math
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from tqdm import tqdm
from multiprocessing import Pool
from utils.constants import *
import random

class LTN_scraper:
    def __init__(self, base_url) -> None:
        self.base_url = base_url
        self.news_url_ls = []
        self.scraped_results = []
        self.errors = []

    def get_news_url_ls(self, page_num, t):

        """scrape news list"""

        news_list = []
        
        for page in range(1, page_num + 1):
            news_list_url = self.base_url + f"/{page}"
            
            r = requests.get(news_list_url, headers = get_random_headers())
            news_data = r.json()

            if isinstance(news_data['data'], list):
                news_list.extend(news_data['data'])
            elif isinstance(news_data['data'], dict):
                news_list.extend(
                    news_data['data'].values()
                )

            time.sleep(random.normalvariate(t, t / 10))

        self.news_url_ls = news_list
        return news_list
    
    def get_news_soup_and_info(self, news):
        url = news['url']

        try:
            
            title = news['title']

            headers = get_random_headers()
            
            body = requests.get(url, headers = headers)
            soup = BeautifulSoup(body.text, 'html.parser')
            
            updated_time = (dt.datetime.now()
                            .replace(tzinfo = ZoneInfo("Asia/Taipei"))
                            .date()
                            .strftime("%Y-%m-%d")
                            + 
                            f" {news['time']}")
            
            
            updated_time = (dt.datetime
                            .strptime(
                            updated_time , "%Y-%m-%d %H:%M"
                            )
            )
            type_cn = news['type_cn']

            return soup, {
                            "title": title,
                            "url": url,
                            "type": type_cn,
                            "updated_time": updated_time,
                            "content": ""
                        }

        except Exception as e:
            return None, {"url": url, "error": str(e)}
    
    class ByCategory:
        """用來取得文章內文的子類別，依照文章種類區分。（因為 ltn 的不同種文章會連接到不同型態的網頁。）"""

        @staticmethod
        def normal(soup):

            article = soup.find("div", class_ = 'text boxTitle boxText')
            content = article.get_text(separator="\n").strip()
            return re.sub("\n+", "\n", content)
            
        
        @staticmethod
        def economics(soup):
        
            article = soup.find("div", class_ = 'whitecon boxTitle boxText')
            content = article.get_text(separator="\n").strip()
            return re.sub("\n+", "\n", content)
            
        
        @staticmethod
        def health(soup):
        
            article = soup.find("div", class_ = 'whitecon article')
            content = article.get_text(separator="\n").strip()
            return re.sub("\n+", "\n", content)
        
        @staticmethod
        def defense(soup):
        
            article = soup.find("div", class_ = 'whitecon article')
            content = article.get_text(separator="\n").strip()
            return re.sub("\n+", "\n", content)
            

    
    def scrape_news_batch(self, t):
        """用 for loop 逐個爬取輸入列表內的新聞連結"""

        for i, news in tqdm(enumerate(self.news_url_ls), total = len(self.news_url_ls)):
            try:
                # * 取得 soup 以及新聞基本資訊
                soup, result = self.get_news_soup_and_info(news)

                # * 依照類別取得文章內容
                if news['url'].startswith("https://news.ltn.com.tw/news/def") :
                    result.update(
                        {
                            "content": self.ByCategory.defense(soup),
                            "len": len(self.ByCategory.defense(soup))
                        }
                    )
                elif news['url'].startswith("https://ec"):
                    result.update(
                        {
                            "content": self.ByCategory.economics(soup),
                            "len": len(self.ByCategory.economics(soup))
                        }
                    )
                elif news['url'].startswith("https://health"):
                    result.update(
                        {
                            "content": self.ByCategory.health(soup),
                            "type": "健康",
                            "len": len(self.ByCategory.health(soup))
                        }
                    )
                elif news['url'].startswith("https://news"):
                    result.update(
                        {
                            "content": self.ByCategory.normal(soup),
                            "len": len(self.ByCategory.normal(soup))
                        }
                    )
                else:
                    result = {"to_pass": 1}

                
                # * 查看 error 是否存在，若存在則放入 errors，否則放入 scraped_results
                if "error" in result:
                    self.errors.append(result)
                # * 非常規新聞頁面，跳過
                elif "to_pass" in result:
                    pass
                # * 其餘結果加入 scraped_results
                else:
                    self.scraped_results.append(result)

            except Exception as e:
                self.errors.append({"url": news['url'], "error": e})

            time.sleep(random.normalvariate(t, t / 10))






    