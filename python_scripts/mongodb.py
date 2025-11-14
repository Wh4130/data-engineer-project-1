from pymongo import MongoClient
from dotenv import load_dotenv
import os, sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def LOAD_TO_MONGODB(collection_name, results):
    load_dotenv()

    client = MongoClient(os.getenv("MONGO_URI"))

        
    try:
        database = client.get_database("news_scrape")
        coll = database.get_collection(collection_name)
        coll.insert_many(results)
        client.close()
    except Exception as e:
        raise Exception("Unable to find the document due to the following error: ", e)

# if __name__ == "__main__":
#     LOAD_TO_MONGODB()