from python_scripts.udn_scraping import UDN_scraper
from python_scripts.mongodb import LOAD_TO_MONGODB
from utils.constants import SCRAPER_SETTINGS
import logging

import asyncio

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def UDN_ETL():
    # --- Instantiate UDN scraper class
    print("start scraping UDN news...")
    udn = UDN_scraper(SCRAPER_SETTINGS['udn']['base_url'])

    print("get news url list...")
    udn.get_news_list(SCRAPER_SETTINGS['udn']['K'], SCRAPER_SETTINGS['udn']['T'])
    
    print("start scraping individual news...")
    udn.scrape_news_batch()

    print("Done scraping! Loading to MongoDB atlas...")

    LOAD_TO_MONGODB("udn", udn.scraped_results)
    print("Done loading!")

    