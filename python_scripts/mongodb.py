from pymongo import MongoClient
from dotenv import load_dotenv
import os
import json

def LOAD_TO_MONGODB():
    load_dotenv()

    client = MongoClient(os.getenv("MONGO_URI"))

    with open("./results.json", 'r') as file:
        news_ls = json.load(file)
        
    try:
        database = client.get_database("news_scrape")
        cna_db = database.get_collection("cna")
        # Query for a movie that has the title 'Back to the Future'
        cna_db.insert_many(news_ls)
        client.close()
    except Exception as e:
        raise Exception("Unable to find the document due to the following error: ", e)

if __name__ == "__main__":
    LOAD_TO_MONGODB()