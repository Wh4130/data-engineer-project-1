from pymongo import MongoClient
from dotenv import load_dotenv
import os, sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


class MongoDbManager:

    def __init__(self) -> None:
        load_dotenv()
        self.client = MongoClient(os.getenv("MONGO_URI"))
    
    def LOAD_TO_MONGODB(self, collection_name, results):

        try:
            database = self.client.get_database("news_scrape")
            coll = database.get_collection(collection_name)
            coll.insert_many(results)
            
        except Exception as e:
            raise Exception("Unable to find the document due to the following error: ", e)
        
    
    def REMOVE_DUPLICATE(self, collection_name):

        try:
            database = self.client.get_database("news_scrape")
            pipelines = [
                {
                    "$group": {
                        "_id": "$url",
                        "count": {"$sum": 1},
                        "all_ids": {"$push": "$_id"}
                    }
                },
                {
                    "$match": {
                        "count": {"$gt": 1}
                    }
                }
            ]

            groups = database[collection_name].aggregate(pipelines)

            ids_to_delete = []

            for group in groups:
                ids_to_delete.extend(group['all_ids'][1:])

            if ids_to_delete != []:
                delete_result = database[collection_name].delete_many(
                    {
                        "_id": {"$in": ids_to_delete}
                    }
                )

                print("result of removing duplicates: ", delete_result)

            return {"removed_count": len(ids_to_delete)}

        except Exception as e:
            raise Exception("Failed to remove duplicates due to the following error: ", e)

    def COUNT_DOCUMENT(self, collection_name):
        db = self.client.get_database("news_scrape")
        return db[collection_name].count_documents({})

    def CLOSE(self):
        self.client.close()