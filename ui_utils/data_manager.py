import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
import datetime as dt
import os
import asyncio
import pandas as pd
import base64

from utils.constants import media_sources
# load_dotenv()


class MongoDbManager:

    # def __init__(self) -> None:
    #     self.client = MongoClient(os.getenv("MONGO_URI"))
    #     self.database = self.client.get_database("news_scrape")


    @st.cache_data
    @staticmethod
    def SELECT_BY_TIME(collection_name: str, 
               time_interval: list[dt.datetime]):
        client = MongoClient(st.secrets["MONGO_URI"])
        database = client.get_database("news_scrape")
        pipeline = [
            {
                "$match": {
                    "title": {
                        "$exists": True
                    },
                    "updated_time": {
                        "$gte": time_interval[0],
                        "$lte": time_interval[1]
                    }
                }
            }
        ]
        df = pd.DataFrame(database[collection_name].aggregate(pipeline))

        client.close()


        # *** udn 文章類別 特別處理
        if collection_name == "udn":
            df['subtype'] = df['type'].apply(lambda x: x[-1])
            df['type'] = df['type'].apply(lambda x: x[1])
        else:
            pass 

        return df
    
    @st.cache_data
    @staticmethod
    def SELECT_ALL_BY_TIME(
            time_interval: list[dt.datetime]):      
        
        ###! 實驗後發現單線程會比較快！驚訝
        async_on = False
        
        collections = media_sources.keys()
        df_list = []

        async def asyncfetch():
            sources = []
            tasks = []
            for collection in collections:
                sources.append(collection)
                tasks.append(asyncio.to_thread(MongoDbManager.SELECT_BY_TIME, collection, time_interval))

            tasks_results = await asyncio.gather(*tasks)
            return (sources, tasks_results)
        
        if async_on:
            # begin = dt.datetime.now()
            sources, tasks_results = asyncio.run(asyncfetch())
            for source, result in zip(sources, tasks_results):
                result['source'] = media_sources[source]['MandName']
                df_list.append(result)
            # end = dt.datetime.now()


        # * 主要會執行這邊（單線程，較快）
        else:
            # begin = dt.datetime.now()
            for collection in collections:
                res = MongoDbManager.SELECT_BY_TIME(
                    collection_name = collection,
                    time_interval = time_interval
                )
                res['source'] = media_sources[collection]['MandName']
                df_list.append(res)
            # end = dt.datetime.now()

        # st.write(f"Time spent: {end - begin}")
        return pd.concat([df for df in df_list if not df.empty], ignore_index = True)
    
class DataTools:

     # --- Transform Picture to Base64
    @staticmethod
    def image_to_b64(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")

class MathTools:
    
    @staticmethod
    def remove_outliers(array: pd.Series):
        """Remove outliers from a DataFrame column using the IQR method."""
        Q1 = array.quantile(0.25)
        Q3 = array.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        filtered_array = array[(array >= lower_bound) & (array <= upper_bound)]
        return filtered_array