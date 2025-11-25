import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import requests
import logging 
import selenium
import datetime as dt
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

class UDN_scraper:
    def __init__(self, base_url) -> None:
        self.base_url = base_url
        self.news_url_ls = []
        self.scraped_results = []
        self.errors = []

    def get_news_list(self, page_num, t):

        """scrape news list"""

        news_list = []
        for page in range(page_num):
            channelId = 1
            cate_id = 0
            type_ = 'breaknews'
            query = f"page={page+1}&channelId={channelId}&cate_id={cate_id}&type={type_}"
            news_list_url = self.base_url + '?' + query
            
            r = requests.get(news_list_url, headers = get_random_headers())
            news_data = r.json()
            news_list.extend(news_data['lists'])

            time.sleep(random.normalvariate(t, t / 10))

        self.news_url_ls = news_list
        return news_list
    
    def scrape_news_batch(self, t):
        """用 for loop 逐個爬取輸入列表內的新聞連結"""
        

        for news in self.news_url_ls:

            url = f"https://udn.com/{news['titleLink']}"

            try:

                updated_time = dt.datetime.strptime(
                    news['time']['date'], "%Y-%m-%d %H:%M")
                title = news['title']

                headers = get_random_headers()
                
                body = requests.get(url, headers = headers)
                soup = BeautifulSoup(body.text, 'html.parser')

                article = soup.find("section", class_ = 'article-content__wrapper')

                cates  = [
                    item.text for item in
                    article.find_all("a", class_ = 'breadcrumb-items')
                ]

                body = article.find("section", class_ = "article-content__editor")
                content = "\n".join(
                    [
                        p.text for p in (body.find_all("p"))
                    ]
                )

                kw_container = article.find("section", id = 'keywords')
                keywords = [
                    kw.text.replace("#", "") for kw in kw_container.find_all("a")
                ]
                
                self.scraped_results.append(
                                        {
                                            "title": title,
                                            "url": url,
                                            "type": cates,
                                            "updated_time": updated_time,
                                            "content": content,
                                            "len": len(content),
                                            "keywords": keywords
                                        }
                                    ) 
                
            except Exception as e:
                self.errors.append(
                    {
                        "url": url,
                        "error": str(e)
                    }
                )
                continue

            time.sleep(random.normalvariate(t, t / 10))

        