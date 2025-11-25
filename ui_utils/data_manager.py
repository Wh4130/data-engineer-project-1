import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
import datetime as dt
import os
import numpy as np
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
    
    @staticmethod
    def SELECT_BY_KEYWORD(collection_name, time_interval: list[dt.datetime], keyword: str):
        client = MongoClient(st.secrets["MONGO_URI"])
        database = client.get_database("news_scrape")

        database[collection_name].create_index([
            ('title', 'text'),
            ('content', 'text')
        ], name='title_content_text_index')

        if keyword == "":
            pipeline = [
                {
                    "$match": {
                        "updated_time": {
                            "$gte": time_interval[0],
                            "$lte": time_interval[1]
                        },
                         "title": {
                        "$exists": True
                        }
                    }
                }
            ]
        else:
            pipeline = [
                {
                    "$match": {
                        # 💡 關鍵字全文搜尋條件 (Text Search must be handled by $text)
                        "$text": {
                            "$search": keyword
                        },
                        
                        # 💡 時間範圍篩選條件
                        "updated_time": {
                            "$gte": time_interval[0],
                            "$lte": time_interval[1]
                        },
                        
                        # 💡 其他條件 (例如確保 title 存在)
                        "title": {
                            "$exists": True
                        }
                    }
                }
                # 您可以根據需要在此處添加其他階段，如 $sort, $limit 等
            ]

        

        df = pd.DataFrame(database[collection_name].aggregate(pipeline))

        if df.empty:
            df = pd.DataFrame(columns = ["_id", "title", "url", "type", "updated_time", "content", "len", "keywords"])

        return pd.DataFrame(df)

    @staticmethod
    def SELECT_BY_QUERY(collection_name, time_interval, keyword_query):
        kw_ls = keyword_query.split(",")
        df_ls = []
        for kw in kw_ls:
            df = MongoDbManager.SELECT_BY_KEYWORD(collection_name, time_interval, kw)
            df_ls.append(df)
        df_final = pd.concat(df_ls)
        df_final = df_final.drop_duplicates(subset = ['_id'])
        
        return df_final

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