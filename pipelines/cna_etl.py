from etl_tasks.cna_scraping import CNA_scraper
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

def CNA_ETL(k = SCRAPER_SETTINGS['cna']['K'] , t = SCRAPER_SETTINGS['cna']['T']):
    try:
        begin = dt.datetime.now()

        # --- Instantiate CNA scraper class
        print("[cna] start scraping CNA news...")
        cna = CNA_scraper(SCRAPER_SETTINGS['cna']['base_url'])

        print("[cna] start driver...")
        cna.start_cna_driver()

        print("[cna] click more button...")
        cna.click_more_btn(k, t)

        print("[cna] get news url list...")
        cna.get_news_url_ls()

        cna.quit()
        
        print("[cna] start scraping individual news...")
        cna.scrape_news_batch(t)

        print("[cna] Done scraping! Loading to MongoDB atlas...")

        mongo = MongoDbManager()
        count_before = mongo.COUNT_DOCUMENT("cna")
        mongo.LOAD_TO_MONGODB("cna", cna.scraped_results)
        
        print("[cna] Done loading! Removing duplicated data...")
        removed_count = mongo.REMOVE_DUPLICATE("cna")["removed_count"]
        count_after = mongo.COUNT_DOCUMENT("cna")

        end = dt.datetime.now()

        return {
            "source": "cna",
            "count_before": count_before,
            "count_after": count_after,
            "removed_count": removed_count,
            "errors": len(cna.errors),
            "duration": end - begin
        }              

    except Exception as e:

        EmailSender.send(os.getenv("RECIPIENT"), f"Error occurred:\n\n {e}")
    