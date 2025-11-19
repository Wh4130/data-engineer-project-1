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


class CNA_scraper:
    def __init__(self, link) -> None:
        self.url     = link 
        
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--headless=new")           # 無頭模式（不開視窗）
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")  # 避免 shared memory 不夠用
        self.options.add_argument("--disable-gpu")            # 在某些 Linux 上避免錯誤

        self.driver  = webdriver.Chrome(self.options)

        self.news_url_ls = []
        self.scraped_results = []
        self.errors = []


        
    def start_cna_driver(self):
        self.driver.get(self.url)
        self.driver.maximize_window()

    def click_more_btn(self, k, t):
        wait = WebDriverWait(self.driver, 10)  # 最長等 10 秒

        for i in range(k):
            try:
                # 滾動到底部
                self.driver.execute_script('window.scrollBy(0,document.body.scrollHeight)') 

                # 明確等待按鈕可被點擊
                btn = wait.until(
                    EC.element_to_be_clickable((By.ID, "SiteContent_uiViewMoreBtn"))
                )
                
                # 如果是最後一次點擊，可以不等待
                if i < k - 1:
                    time.sleep(t) # 如果仍要強制等待，請保留
                
                btn.click()
                
            except Exception as e:
                # 如果按鈕消失 (代表已經加載完所有內容) 或出現其他錯誤，則退出迴圈
                print(f"Click more button failed or finished: {e}")
                break

    def get_news_url_ls(self):
        """取得所有新聞連結"""
        container = self.driver.find_element(By.ID, "jsMainList")
        news = container.find_elements(by = By.TAG_NAME, value = "li")
        news_url_ls = [_.find_element(By.TAG_NAME, "a").get_attribute("href") for _ in news]
        self.news_url_ls = news_url_ls
        return news_url_ls
    
    def quit(self):
        self.driver.quit()
        print("web driver quit successfully.")

    def scrape_news_batch(self, t):
        """用 for loop 逐個爬取輸入列表內的新聞連結"""
        


        for url in self.news_url_ls:

            try:

                headers = get_random_headers()
                
                body = requests.get(url, headers = headers)
                soup = BeautifulSoup(body.text, 'html.parser')

                article = soup.find("article")
                title  = article.attrs["data-title"]
                cate  = article.attrs["data-origin-type-name"]
                url    = article.attrs["data-canonical-url"]


                updated_time = (article
                        .find("div", class_ = "updatetime")
                        .find_all("span")[0]
                        .text
                        )

                updated_time = dt.datetime.strptime(updated_time, "%Y/%m/%d %H:%M")
                

                body = article.find("div", class_ = "paragraph")
                content = "\n".join(
                    [
                        p.text for p in (body.find_all("p"))
                    ]
                )
                keywords = [
                    kw.text for kw in article.find_all("div", class_ = "keywordTag")
                ]
                
                self.scraped_results.append(
                                        {
                                            "title": title,
                                            "url": url,
                                            "type": cate,
                                            "updated_time": updated_time,
                                            "content": content,
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
        
        return self.scraped_results



if __name__ == "__main__":
    pass





    