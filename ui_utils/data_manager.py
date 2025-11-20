import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
import datetime as dt
import os
import pandas as pd
import base64

from utils.constants import media_sources

class MongoDbManager:

    def __init__(self) -> None:
        load_dotenv()
        self.client = MongoClient(os.getenv("MONGO_URI"))
        self.database = self.client.get_database("news_scrape")


    @st.cache_data
    def SELECT_BY_TIME(_self, 
               collection_name: str, 
               time_interval: list[dt.datetime]):
        pipeline = [
            {
                "$match": {
                    "title": {
                        "$exists": True
                    }
                },
                "$match": {
                    "updated_time": {
                        "$gte": time_interval[0],
                        "$lte": time_interval[1]
                    }
                }
            }
        ]
        df = pd.DataFrame(_self.database[collection_name].aggregate(pipeline))

        # *** udn 文章類別 特別處理
        if collection_name == "udn":
            df['subtype'] = df['type'].apply(lambda x: x[-1])
            df['type'] = df['type'].apply(lambda x: x[1])
        else:
            pass 

        return df
    
    @st.cache_data
    def SELECT_ALL_BY_TIME(
            _self, 
            time_interval: list[dt.datetime]):      
        
        collections = _self.database.list_collection_names()
        df_list = []
        for collection in collections:
            res = _self.SELECT_BY_TIME(
                collection_name = collection,
                time_interval = time_interval
            )
            res['source'] = media_sources[collection]['MandName']
            df_list.append(res)

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