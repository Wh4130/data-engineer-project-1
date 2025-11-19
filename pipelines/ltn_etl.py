from etl_tasks.ltn_scraping import LTN_scraper
from etl_tasks.mongodb import MongoDbManager
from utils.constants import SCRAPER_SETTINGS
from utils.email_sender import EmailSender
import logging
import datetime as dt

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()


import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def LTN_ETL(k = SCRAPER_SETTINGS['udn']['K'], t = SCRAPER_SETTINGS['udn']['T']):
    try:
        begin = dt.datetime.now()

        # --- Instantiate LTN scraper class
        print("[ltn] start scraping LTN news...")
        ltn = LTN_scraper(SCRAPER_SETTINGS['ltn']['base_url'])

        print("[ltn] get news url list...")
        ltn.get_news_url_ls(k, t)
        
        print("[ltn] start scraping individual news...")
        ltn.scrape_news_batch(t)

        print("[ltn] Done scraping! Loading to MongoDB atlas...")

        mongo = MongoDbManager()
        count_before = mongo.COUNT_DOCUMENT("ltn")
        mongo.LOAD_TO_MONGODB("ltn", ltn.scraped_results)
        
        print("[ltn] Done loading! Removing duplicated data...")
        removed_count = mongo.REMOVE_DUPLICATE("ltn")["removed_count"]
        count_after = mongo.COUNT_DOCUMENT("ltn")

        end = dt.datetime.now()

        return {
            "source": "ltn",
            "count_before": count_before,
            "count_after": count_after,
            "removed_count": removed_count,
            "errors": len(ltn.errors),
            "duration": end - begin
        }              

    except Exception as e:

        EmailSender.send(os.getenv("RECIPIENT"), f"Error occurred:\n\n {e}")
    