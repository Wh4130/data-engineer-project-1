from python_scripts.cna_scraping import CNA_scraper
from python_scripts.mongodb import MongoDbManager
from utils.constants import SCRAPER_SETTINGS
from utils.email_sender import EmailSender
import logging

import asyncio
from dotenv import load_dotenv

load_dotenv()

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def CNA_ETL(k = SCRAPER_SETTINGS['cna']['K'] , t = SCRAPER_SETTINGS['cna']['T']):
    try:
        # --- Instantiate CNA scraper class
        print("start scraping CNA news...")
        cna = CNA_scraper(SCRAPER_SETTINGS['cna']['base_url'])

        print("start driver...")
        cna.start_cna_driver()

        print("click more button...")
        cna.click_more_btn(k, t)

        print("get news url list...")
        cna.get_news_url_ls()

        cna.quit()
        
        print("start scraping individual news...")
        cna.scrape_news_batch()

        print("Done scraping! Loading to MongoDB atlas...")

        mongo = MongoDbManager()
        count_before = mongo.COUNT_DOCUMENT("cna")
        mongo.LOAD_TO_MONGODB("cna", cna.scraped_results)
        
        print("Done loading! Removing duplicated data...")
        removed_count = mongo.REMOVE_DUPLICATE("cna")["removed_count"]
        count_after = mongo.COUNT_DOCUMENT("cna")

        print("Sending email...")
        body = EmailSender.template("CNA", count_before, count_after, removed_count)
        EmailSender.send(os.getenv("RECIPIENT"), body)

        print("Done!")

    except Exception as e:

        EmailSender.send(os.getenv("RECIPIENT"), f"Error occurred:\n\n {e}")
    