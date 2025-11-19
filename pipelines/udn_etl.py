from etl_tasks.udn_scraping import UDN_scraper
from etl_tasks.mongodb import MongoDbManager
from utils.constants import SCRAPER_SETTINGS
from utils.email_sender import EmailSender
import logging
import datetime as dt

import asyncio
import sys, os

from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def UDN_ETL(k = SCRAPER_SETTINGS['udn']['K'], t = SCRAPER_SETTINGS['udn']['T']):
    try:
        begin = dt.datetime.now()
        # --- Instantiate UDN scraper class
        print("[udn] start scraping UDN news...")
        udn = UDN_scraper(SCRAPER_SETTINGS['udn']['base_url'])

        print("[udn] get news url list...")
        udn.get_news_list(k, t)
        
        print("[udn] start scraping individual news...")
        udn.scrape_news_batch(t)

        print("[udn] Done scraping! Loading to MongoDB atlas...")

        mongo = MongoDbManager()
        count_before = mongo.COUNT_DOCUMENT("udn")
        mongo.LOAD_TO_MONGODB("udn", udn.scraped_results)
        
        print("[udn] Done loading! Removing duplicated data...")
        removed_count = mongo.REMOVE_DUPLICATE("udn")["removed_count"]
        count_after = mongo.COUNT_DOCUMENT("udn")

        end = dt.datetime.now()

        return {
                    "source": "cna",
                    "count_before": count_before,
                    "count_after": count_after,
                    "removed_count": removed_count,
                    "errors": len(udn.errors),
                    "duration": end - begin
                }   

    except Exception as e:

        EmailSender.send(os.getenv("RECIPIENT"), f"Error occurred:\n\n {e}")
    