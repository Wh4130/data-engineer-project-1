from python_scripts.udn_scraping import UDN_scraper
from python_scripts.mongodb import MongoDbManager
from utils.constants import SCRAPER_SETTINGS
from utils.email_sender import EmailSender
import logging

import asyncio
from dotenv import load_dotenv

load_dotenv()

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def UDN_ETL(k = SCRAPER_SETTINGS['udn']['K'], t = SCRAPER_SETTINGS['udn']['T']):
    try:
        # --- Instantiate UDN scraper class
        print("start scraping UDN news...")
        udn = UDN_scraper(SCRAPER_SETTINGS['udn']['base_url'])

        print("get news url list...")
        udn.get_news_list(k, t)
        
        print("start scraping individual news...")
        udn.scrape_news_batch()

        print("Done scraping! Loading to MongoDB atlas...")

        mongo = MongoDbManager()
        count_before = mongo.COUNT_DOCUMENT("udn")
        mongo.LOAD_TO_MONGODB("udn", udn.scraped_results)
        
        print("Done loading! Removing duplicated data...")
        removed_count = mongo.REMOVE_DUPLICATE("udn")["removed_count"]
        count_after = mongo.COUNT_DOCUMENT("udn")

        print("Sending email...")
        body = EmailSender.template("UDN", count_before, count_after, removed_count)
        EmailSender.send(os.getenv("RECIPIENT"), body)

        print("Done!")

    except Exception as e:

        EmailSender.send(os.getenv("RECIPIENT"), f"Error occurred:\n\n {e}")
    